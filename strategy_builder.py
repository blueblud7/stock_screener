import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class ConditionType(Enum):
    """조건 타입 정의"""
    BOLLINGER_BAND = "bollinger_band"
    RSI = "rsi"
    MACD = "macd"
    MOVING_AVERAGE = "moving_average"
    VOLUME = "volume"
    PRICE_ACTION = "price_action"
    CUSTOM = "custom"

class Operator(Enum):
    """연산자 정의"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CROSS_ABOVE = "cross_above"
    CROSS_BELOW = "cross_below"
    BREAKOUT = "breakout"
    SUPPORT = "support"

@dataclass
class Condition:
    """단일 조건 정의"""
    name: str
    condition_type: ConditionType
    operator: Operator
    value: float
    description: str
    parameters: Dict[str, Any] = None

class StrategyBuilder:
    """조건식 조합 전략 빌더"""
    
    def __init__(self):
        self.conditions = []
        self.combination_logic = "AND"  # AND, OR
        
    def add_condition(self, condition: Condition):
        """조건 추가"""
        self.conditions.append(condition)
        
    def set_combination_logic(self, logic: str):
        """조건 조합 방식 설정 (AND/OR)"""
        self.combination_logic = logic
        
    def evaluate_strategy(self, data: pd.DataFrame) -> bool:
        """전략 평가"""
        if data is None or data.empty or len(data) < 2:
            return False
            
        results = []
        
        for condition in self.conditions:
            result = self._evaluate_condition(data, condition)
            results.append(result)
            
        if self.combination_logic == "AND":
            return all(results)
        else:  # OR
            return any(results) if results else False
    
    def _evaluate_condition(self, data: pd.DataFrame, condition: Condition) -> bool:
        """개별 조건 평가"""
        try:
            if condition.condition_type == ConditionType.BOLLINGER_BAND:
                return self._evaluate_bollinger_band(data, condition)
            elif condition.condition_type == ConditionType.RSI:
                return self._evaluate_rsi(data, condition)
            elif condition.condition_type == ConditionType.MACD:
                return self._evaluate_macd(data, condition)
            elif condition.condition_type == ConditionType.MOVING_AVERAGE:
                return self._evaluate_moving_average(data, condition)
            elif condition.condition_type == ConditionType.VOLUME:
                return self._evaluate_volume(data, condition)
            elif condition.condition_type == ConditionType.PRICE_ACTION:
                return self._evaluate_price_action(data, condition)
            else:
                return False
        except Exception as e:
            print(f"조건 평가 오류 ({condition.name}): {str(e)}")
            return False
    
    def _evaluate_bollinger_band(self, data: pd.DataFrame, condition: Condition) -> bool:
        """볼린저 밴드 조건 평가"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if condition.operator == Operator.BREAKOUT:
            # 상단 밴드 돌파
            return (prev['Close'] <= prev['BB_Upper']) and (latest['Close'] > latest['BB_Upper'])
        elif condition.operator == Operator.SUPPORT:
            # 하단 밴드 지지
            return (prev['Close'] <= prev['BB_Lower']) and (latest['Close'] > latest['BB_Lower'])
        elif condition.operator == Operator.GREATER_THAN:
            # 현재가가 상단 밴드보다 높음
            return latest['Close'] > latest['BB_Upper']
        elif condition.operator == Operator.LESS_THAN:
            # 현재가가 하단 밴드보다 낮음
            return latest['Close'] < latest['BB_Lower']
        
        return False
    
    def _evaluate_rsi(self, data: pd.DataFrame, condition: Condition) -> bool:
        """RSI 조건 평가"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if condition.operator == Operator.GREATER_THAN:
            return latest['RSI'] > condition.value
        elif condition.operator == Operator.LESS_THAN:
            return latest['RSI'] < condition.value
        elif condition.operator == Operator.CROSS_ABOVE:
            # RSI가 특정 값을 상향 돌파
            return (prev['RSI'] <= condition.value) and (latest['RSI'] > condition.value)
        elif condition.operator == Operator.CROSS_BELOW:
            # RSI가 특정 값을 하향 돌파
            return (prev['RSI'] >= condition.value) and (latest['RSI'] < condition.value)
        
        return False
    
    def _evaluate_macd(self, data: pd.DataFrame, condition: Condition) -> bool:
        """MACD 조건 평가"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if condition.operator == Operator.CROSS_ABOVE:
            # MACD가 시그널선 상향 돌파
            return (prev['MACD'] <= prev['MACD_Signal']) and (latest['MACD'] > latest['MACD_Signal'])
        elif condition.operator == Operator.CROSS_BELOW:
            # MACD가 시그널선 하향 돌파
            return (prev['MACD'] >= prev['MACD_Signal']) and (latest['MACD'] < latest['MACD_Signal'])
        elif condition.operator == Operator.GREATER_THAN:
            return latest['MACD'] > condition.value
        elif condition.operator == Operator.LESS_THAN:
            return latest['MACD'] < condition.value
        
        return False
    
    def _evaluate_moving_average(self, data: pd.DataFrame, condition: Condition) -> bool:
        """이동평균 조건 평가"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if condition.operator == Operator.CROSS_ABOVE:
            if condition.parameters and 'ma_type' in condition.parameters:
                if condition.parameters['ma_type'] == 'golden_cross':
                    # 골든 크로스 (20일선이 50일선 상향 돌파)
                    return (prev['SMA_20'] <= prev['SMA_50']) and (latest['SMA_20'] > latest['SMA_50'])
                elif condition.parameters['ma_type'] == 'price_above_ma20':
                    # 주가가 20일선 상향 돌파
                    return (prev['Close'] <= prev['SMA_20']) and (latest['Close'] > latest['SMA_20'])
        elif condition.operator == Operator.GREATER_THAN:
            # 주가가 이동평균선보다 높음
            if condition.parameters and 'period' in condition.parameters:
                ma_col = f"SMA_{condition.parameters['period']}"
                if ma_col in data.columns:
                    return latest['Close'] > latest[ma_col]
        
        return False
    
    def _evaluate_volume(self, data: pd.DataFrame, condition: Condition) -> bool:
        """거래량 조건 평가"""
        latest = data.iloc[-1]
        
        if condition.operator == Operator.GREATER_THAN:
            if 'Volume_SMA' in data.columns:
                return latest['Volume'] > latest['Volume_SMA'] * condition.value
            else:
                # 이전 N일 평균 대비
                n_days = condition.parameters.get('period', 20) if condition.parameters else 20
                avg_volume = data['Volume'].rolling(window=n_days).mean().iloc[-1]
                return latest['Volume'] > avg_volume * condition.value
        
        return False
    
    def _evaluate_price_action(self, data: pd.DataFrame, condition: Condition) -> bool:
        """가격 액션 조건 평가"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        if condition.operator == Operator.GREATER_THAN:
            if condition.parameters and 'type' in condition.parameters:
                if condition.parameters['type'] == 'daily_change':
                    # 일일 변화율
                    change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                    return change_pct > condition.value
                elif condition.parameters['type'] == 'gap_up':
                    # 갭 상승
                    gap_pct = ((latest['Open'] - prev['Close']) / prev['Close']) * 100
                    return gap_pct > condition.value
        
        return False

class PresetStrategies:
    """사전 정의된 전략들"""
    
    @staticmethod
    def momentum_breakout() -> StrategyBuilder:
        """모멘텀 돌파 전략"""
        strategy = StrategyBuilder()
        
        # 볼린저 밴드 상단 돌파
        bb_condition = Condition(
            name="BB 상단 돌파",
            condition_type=ConditionType.BOLLINGER_BAND,
            operator=Operator.BREAKOUT,
            value=0,
            description="볼린저 밴드 상단을 돌파"
        )
        
        # RSI 70 이하 (과매수 아님)
        rsi_condition = Condition(
            name="RSI < 70",
            condition_type=ConditionType.RSI,
            operator=Operator.LESS_THAN,
            value=70,
            description="RSI가 70 이하 (과매수 구간 아님)"
        )
        
        # 거래량 급증
        volume_condition = Condition(
            name="거래량 급증",
            condition_type=ConditionType.VOLUME,
            operator=Operator.GREATER_THAN,
            value=1.5,
            description="평균 거래량의 1.5배 이상"
        )
        
        strategy.add_condition(bb_condition)
        strategy.add_condition(rsi_condition)
        strategy.add_condition(volume_condition)
        strategy.set_combination_logic("AND")
        
        return strategy
    
    @staticmethod
    def oversold_reversal() -> StrategyBuilder:
        """과매도 반전 전략"""
        strategy = StrategyBuilder()
        
        # RSI 과매도 구간에서 반등
        rsi_condition = Condition(
            name="RSI 과매도 반등",
            condition_type=ConditionType.RSI,
            operator=Operator.CROSS_ABOVE,
            value=30,
            description="RSI가 30을 상향 돌파"
        )
        
        # 볼린저 밴드 하단 지지
        bb_condition = Condition(
            name="BB 하단 지지",
            condition_type=ConditionType.BOLLINGER_BAND,
            operator=Operator.SUPPORT,
            value=0,
            description="볼린저 밴드 하단에서 지지"
        )
        
        strategy.add_condition(rsi_condition)
        strategy.add_condition(bb_condition)
        strategy.set_combination_logic("AND")
        
        return strategy
    
    @staticmethod
    def golden_cross() -> StrategyBuilder:
        """골든 크로스 전략"""
        strategy = StrategyBuilder()
        
        # 골든 크로스
        ma_condition = Condition(
            name="골든 크로스",
            condition_type=ConditionType.MOVING_AVERAGE,
            operator=Operator.CROSS_ABOVE,
            value=0,
            description="20일 이동평균이 50일 이동평균을 상향 돌파",
            parameters={'ma_type': 'golden_cross'}
        )
        
        # MACD 상승 전환
        macd_condition = Condition(
            name="MACD 상승 전환",
            condition_type=ConditionType.MACD,
            operator=Operator.CROSS_ABOVE,
            value=0,
            description="MACD가 시그널선을 상향 돌파"
        )
        
        strategy.add_condition(ma_condition)
        strategy.add_condition(macd_condition)
        strategy.set_combination_logic("AND")
        
        return strategy

def get_strategy_description(strategy: StrategyBuilder) -> str:
    """전략 설명 텍스트 생성"""
    description = f"조합 방식: {strategy.combination_logic}\n\n조건들:\n"
    
    for i, condition in enumerate(strategy.conditions, 1):
        description += f"{i}. {condition.name}: {condition.description}\n"
    
    return description 