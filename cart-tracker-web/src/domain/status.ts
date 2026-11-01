import type { PositionFix } from './types'

// Устаревание отметки.
//
// Отметка считается свежей, пока её возраст не превысил порог: источник
// присылает координаты с известной частотой, и пропуск одного-двух пакетов
// не должен превращать тележку в «потерянную». Порог задаётся в миллисекундах
// и подбирается под частоту источника.

/** Сколько миллисекунд отметка остаётся свежей. 2.5 с ≈ два пропуска при 1 Гц. */
export const STALE_AFTER_MS = 2500

export type Freshness = 'fresh' | 'stale'

/** Возраст отметки на момент nowMs. Может быть отрицательным при рассинхроне часов. */
export function ageMs(fix: PositionFix, nowMs: number): number {
	return nowMs - Date.parse(fix.ts)
}

/** Свежесть отметки: на границе порога она ещё свежая, стареет строго после. */
export function freshness(
	fix: PositionFix,
	nowMs: number,
	staleAfterMs: number = STALE_AFTER_MS,
): Freshness {
	return ageMs(fix, nowMs) > staleAfterMs ? 'stale' : 'fresh'
}

/** Сколько отметок устарело на момент nowMs. */
export function countStale(
	positions: Iterable<PositionFix>,
	nowMs: number,
	staleAfterMs: number = STALE_AFTER_MS,
): number {
	let count = 0
	for (const fix of positions) {
		if (freshness(fix, nowMs, staleAfterMs) === 'stale') count += 1
	}
	return count
}
