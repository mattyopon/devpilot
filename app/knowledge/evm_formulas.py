"""EVM (Earned Value Management) 計算式.

EVMの全指標計算ロジックを提供する。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EVMInput:
    """EVM計算入力."""

    bac: float  # Budget at Completion
    pv: float   # Planned Value
    ev: float   # Earned Value
    ac: float   # Actual Cost


@dataclass(frozen=True)
class EVMResult:
    """EVM計算結果."""

    bac: float
    pv: float
    ev: float
    ac: float
    sv: float
    cv: float
    spi: float
    cpi: float
    eac: float
    etc: float
    vac: float
    tcpi: float


def calculate_schedule_variance(ev: float, pv: float) -> float:
    """スケジュール差異 (SV = EV - PV)."""
    return ev - pv


def calculate_cost_variance(ev: float, ac: float) -> float:
    """コスト差異 (CV = EV - AC)."""
    return ev - ac


def calculate_spi(ev: float, pv: float) -> float:
    """スケジュール効率指数 (SPI = EV / PV).

    SPI > 1.0: 予定より前倒し
    SPI = 1.0: 予定通り
    SPI < 1.0: 遅延
    """
    if pv == 0:
        return 0.0
    return ev / pv


def calculate_cpi(ev: float, ac: float) -> float:
    """コスト効率指数 (CPI = EV / AC).

    CPI > 1.0: 予算内
    CPI = 1.0: 予算通り
    CPI < 1.0: 予算超過
    """
    if ac == 0:
        return 0.0
    return ev / ac


def calculate_eac(bac: float, cpi: float) -> float:
    """完成時総見積もり (EAC = BAC / CPI)."""
    if cpi == 0:
        return 0.0
    return bac / cpi


def calculate_etc(eac: float, ac: float) -> float:
    """残作業見積もり (ETC = EAC - AC)."""
    return eac - ac


def calculate_vac(bac: float, eac: float) -> float:
    """完了時差異 (VAC = BAC - EAC)."""
    return bac - eac


def calculate_tcpi(bac: float, ev: float, ac: float) -> float:
    """残作業効率指数 (TCPI = (BAC - EV) / (BAC - AC)).

    残りの予算で完了するために必要な効率。
    TCPI > 1.0: より効率的に作業する必要がある
    TCPI = 1.0: 現在のペースで達成可能
    TCPI < 1.0: 余裕がある
    """
    denominator = bac - ac
    if denominator == 0:
        return 0.0
    return (bac - ev) / denominator


def calculate_evm(evm_input: EVMInput) -> EVMResult:
    """EVM全指標を計算."""
    sv = calculate_schedule_variance(evm_input.ev, evm_input.pv)
    cv = calculate_cost_variance(evm_input.ev, evm_input.ac)
    spi = calculate_spi(evm_input.ev, evm_input.pv)
    cpi = calculate_cpi(evm_input.ev, evm_input.ac)
    eac = calculate_eac(evm_input.bac, cpi)
    etc = calculate_etc(eac, evm_input.ac)
    vac = calculate_vac(evm_input.bac, eac)
    tcpi = calculate_tcpi(evm_input.bac, evm_input.ev, evm_input.ac)

    return EVMResult(
        bac=evm_input.bac,
        pv=evm_input.pv,
        ev=evm_input.ev,
        ac=evm_input.ac,
        sv=sv,
        cv=cv,
        spi=spi,
        cpi=cpi,
        eac=eac,
        etc=etc,
        vac=vac,
        tcpi=tcpi,
    )


def interpret_health(spi: float, cpi: float) -> str:
    """プロジェクト健全性を解釈.

    Returns:
        健全性ステータス文字列
    """
    if spi >= 0.95 and cpi >= 0.95:
        return "HEALTHY"
    if spi >= 0.8 and cpi >= 0.8:
        return "WARNING"
    return "CRITICAL"


def interpret_spi(spi: float) -> str:
    """SPI解釈."""
    if spi >= 1.0:
        return "予定通りまたは前倒し"
    if spi >= 0.9:
        return "軽微な遅延"
    if spi >= 0.8:
        return "遅延（対策要）"
    return "深刻な遅延（緊急対応要）"


def interpret_cpi(cpi: float) -> str:
    """CPI解釈."""
    if cpi >= 1.0:
        return "予算内"
    if cpi >= 0.9:
        return "軽微な超過"
    if cpi >= 0.8:
        return "予算超過（対策要）"
    return "深刻な予算超過（緊急対応要）"
