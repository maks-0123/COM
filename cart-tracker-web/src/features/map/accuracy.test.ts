import { describe, expect, it } from 'vitest'
import { STALE_AFTER_MS } from '../../domain/status'
import type { PositionFix, PositioningMethod } from '../../domain/types'
import { accuracyColor, accuracyStyle, methodLabel, METHOD_COLOR } from './accuracy'

const T0 = Date.parse('2026-10-28T09:00:00Z')

function fix(overrides: Partial<PositionFix> = {}): PositionFix {
	return {
		cartId: 'c1',
		ts: new Date(T0).toISOString(),
		position: { x: 0, y: 0 },
		accuracyM: 10,
		method: 'rssi-multilateration',
		...overrides,
	}
}

describe('accuracyColor', () => {
	it.each([
		['rssi-multilateration', '#2563eb'],
		['ecid-ta', '#d97706'],
		['cell-id', '#dc2626'],
		['simulated', '#7c3aed'],
		['unknown', '#64748b'],
	] as const)('метод %s → %s', (method: PositioningMethod, color: string) => {
		expect(accuracyColor(method)).toBe(color)
	})

	it('без метода — серый, как unknown', () => {
		expect(accuracyColor(undefined)).toBe(METHOD_COLOR.unknown)
	})
})

describe('methodLabel', () => {
	it('переводит метод в подпись для подсказки', () => {
		expect(methodLabel('rssi-multilateration')).toBe('RSSI')
		expect(methodLabel('ecid-ta')).toBe('ECID+TA')
		expect(methodLabel('cell-id')).toBe('Cell ID')
		expect(methodLabel('simulated')).toBe('симуляция')
	})

	it('без метода — понятная подпись, а не undefined', () => {
		expect(methodLabel(undefined)).toBe('метод неизвестен')
	})
})

describe('accuracyStyle', () => {
	it('без accuracyM круга нет', () => {
		expect(accuracyStyle(fix({ accuracyM: undefined }), T0)).toBeNull()
	})

	it('нулевая точность не рисуется', () => {
		expect(accuracyStyle(fix({ accuracyM: 0 }), T0)).toBeNull()
	})

	it('отрицательная точность не рисуется', () => {
		expect(accuracyStyle(fix({ accuracyM: -5 }), T0)).toBeNull()
	})

	it('свежая отметка: заметная обводка, прозрачная заливка, пунктир', () => {
		expect(accuracyStyle(fix(), T0)).toEqual({
			color: '#2563eb',
			opacity: 0.5,
			fillOpacity: 0.1,
			dashArray: '4 4',
		})
	})

	it('устаревшая отметка гаснет', () => {
		const style = accuracyStyle(fix(), T0 + STALE_AFTER_MS + 1)
		expect(style).not.toBeNull()
		expect(style?.opacity).toBeLessThan(0.5)
		expect(style?.fillOpacity).toBeLessThan(0.1)
	})

	it('цвет зависит от метода, а не от свежести', () => {
		const stale = accuracyStyle(fix({ method: 'cell-id' }), T0 + STALE_AFTER_MS + 1)
		expect(stale?.color).toBe('#dc2626')
	})
})
