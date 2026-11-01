import { describe, expect, it } from 'vitest'
import { sourceModeFromUrl } from './registry'

describe('sourceModeFromUrl', () => {
	it('по умолчанию — проигрывание записи', () => {
		expect(sourceModeFromUrl('')).toBe('replay')
		expect(sourceModeFromUrl('?foo=bar')).toBe('replay')
	})

	it('?source=live включает живой режим', () => {
		expect(sourceModeFromUrl('?source=live')).toBe('live')
	})

	it('неизвестное значение не ломает демо', () => {
		expect(sourceModeFromUrl('?source=websocket')).toBe('replay')
	})
})
