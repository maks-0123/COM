import { freshness } from '../../domain/status'
import type { PositionFix, PositioningMethod } from '../../domain/types'

// Внешний вид круга точности.
//
// Здесь только вычисления, без React и Leaflet: так их можно покрыть тестами,
// а сам слой остаётся тонким — взять стиль и нарисовать Circle.

/** Цвет по методу позиционирования: чем грубее метод, тем тревожнее цвет. */
export const METHOD_COLOR: Record<PositioningMethod, string> = {
	'rssi-multilateration': '#2563eb',
	'ecid-ta': '#d97706',
	'cell-id': '#dc2626',
	simulated: '#7c3aed',
	unknown: '#64748b',
}

export type AccuracyStyle = {
	color: string
	/** Прозрачность обводки. */
	opacity: number
	/** Прозрачность заливки: круг не должен закрывать подложку. */
	fillOpacity: number
	dashArray: string
}

// Свежая отметка читается, устаревшая почти растворяется.
const FRESH = { opacity: 0.5, fillOpacity: 0.1 }
const STALE = { opacity: 0.15, fillOpacity: 0.03 }

export function accuracyColor(method: PositioningMethod | undefined): string {
	return METHOD_COLOR[method ?? 'unknown']
}

/** Человекочитаемое название метода для подсказок на карте. */
export const METHOD_LABEL: Record<PositioningMethod, string> = {
	'rssi-multilateration': 'RSSI',
	'ecid-ta': 'ECID+TA',
	'cell-id': 'Cell ID',
	simulated: 'симуляция',
	unknown: 'метод неизвестен',
}

export function methodLabel(method: PositioningMethod | undefined): string {
	return METHOD_LABEL[method ?? 'unknown']
}

/**
 * Стиль круга точности на момент nowMs.
 * null — рисовать нечего: точность не указана или вырождена.
 */
export function accuracyStyle(fix: PositionFix, nowMs: number): AccuracyStyle | null {
	if (fix.accuracyM === undefined || fix.accuracyM <= 0) return null

	const tone = freshness(fix, nowMs) === 'stale' ? STALE : FRESH
	return {
		color: accuracyColor(fix.method),
		opacity: tone.opacity,
		fillOpacity: tone.fillOpacity,
		dashArray: '4 4',
	}
}
