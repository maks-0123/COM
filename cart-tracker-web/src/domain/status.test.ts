import { describe, expect, it } from 'vitest'
import { ageMs, countStale, freshness, STALE_AFTER_MS } from './status'
import type { PositionFix } from './types'

const T0 = Date.parse('2026-10-28T09:00:00Z')

function fix(ts: number): PositionFix {
	return { cartId: 'c1', ts: new Date(ts).toISOString(), position: { x: 0, y: 0 } }
}

describe('freshness', () => {
	it('отметка свежая, пока возраст меньше порога', () => {
		expect(freshness(fix(T0), T0 + STALE_AFTER_MS - 1)).toBe('fresh')
	})

	it('на самой границе порога ещё свежая', () => {
		expect(freshness(fix(T0), T0 + STALE_AFTER_MS)).toBe('fresh')
	})

	it('стареет строго после порога', () => {
		expect(freshness(fix(T0), T0 + STALE_AFTER_MS + 1)).toBe('stale')
	})

	it('принимает собственный порог', () => {
		expect(freshness(fix(T0), T0 + 100, 50)).toBe('stale')
		expect(freshness(fix(T0), T0 + 100, 500)).toBe('fresh')
	})

	it('отметка из будущего не считается устаревшей', () => {
		expect(freshness(fix(T0 + 1000), T0)).toBe('fresh')
	})
})

describe('ageMs', () => {
	it('считает возраст в миллисекундах', () => {
		expect(ageMs(fix(T0), T0 + 1500)).toBe(1500)
	})

	it('для отметки из будущего возраст отрицательный', () => {
		expect(ageMs(fix(T0 + 500), T0)).toBe(-500)
	})
})

describe('countStale', () => {
	it('считает только устаревшие отметки', () => {
		const fresh = fix(T0)
		const stale = fix(T0 - STALE_AFTER_MS - 1)
		expect(countStale([fresh, fresh], T0)).toBe(0)
		expect(countStale([fresh, stale], T0)).toBe(1)
		expect(countStale([stale, stale], T0)).toBe(2)
	})

	it('на пустом наборе возвращает ноль', () => {
		expect(countStale([], T0)).toBe(0)
	})

	it('принимает собственный порог', () => {
		const fix1 = fix(T0)
		expect(countStale([fix1], T0 + 100, 50)).toBe(1)
		expect(countStale([fix1], T0 + 100, 500)).toBe(0)
	})
})
