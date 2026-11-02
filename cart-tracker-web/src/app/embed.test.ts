import { describe, expect, it } from 'vitest'
import { readEmbedOptions } from './embed'

describe('readEmbedOptions', () => {
	it('без параметров — всё по умолчанию', () => {
		expect(readEmbedOptions('')).toEqual({
			embed: false,
			theme: 'light',
			sourceMode: 'replay',
			dataUrl: null,
		})
	})

	it('включает embed по 1, true, yes, on', () => {
		for (const value of ['1', 'true', 'yes', 'on', 'TRUE']) {
			expect(readEmbedOptions(`?embed=${value}`).embed).toBe(true)
		}
	})

	it('не включает embed по 0 и мусору', () => {
		expect(readEmbedOptions('?embed=0').embed).toBe(false)
		expect(readEmbedOptions('?embed=maybe').embed).toBe(false)
	})

	it('понимает тёмную тему и игнорирует неизвестную', () => {
		expect(readEmbedOptions('?theme=dark').theme).toBe('dark')
		expect(readEmbedOptions('?theme=neon').theme).toBe('light')
	})

	it('передаёт режим live', () => {
		expect(readEmbedOptions('?source=live').sourceMode).toBe('live')
		expect(readEmbedOptions('?source=other').sourceMode).toBe('replay')
	})

	it('читает адрес снимка и превращает пустой в null', () => {
		expect(readEmbedOptions('?data=/map/data/live.json').dataUrl).toBe(
			'/map/data/live.json',
		)
		expect(readEmbedOptions('?data=').dataUrl).toBeNull()
		expect(readEmbedOptions('?data=%20%20').dataUrl).toBeNull()
	})

	it('понимает всё вместе', () => {
		expect(
			readEmbedOptions('?embed=1&theme=dark&source=live&data=/map/x.json'),
		).toEqual({
			embed: true,
			theme: 'dark',
			sourceMode: 'live',
			dataUrl: '/map/x.json',
		})
	})
})
