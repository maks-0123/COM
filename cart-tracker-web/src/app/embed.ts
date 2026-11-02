import { sourceModeFromUrl, type SourceMode } from '../sources/registry'

export type EmbedTheme = 'light' | 'dark'

export type EmbedOptions = {
	embed: boolean
	theme: EmbedTheme
	sourceMode: SourceMode
	dataUrl: string | null
}
const TRUE_VALUES = new Set(['1', 'true', 'yes', 'on'])

export function readEmbedOptions(search: string): EmbedOptions {
	const params = new URLSearchParams(search)
	return {
		embed: TRUE_VALUES.has((params.get('embed') ?? '').toLowerCase()),
		theme: params.get('theme') === 'dark' ? 'dark' : 'light',
		sourceMode: sourceModeFromUrl(search),

		dataUrl: params.get('data')?.trim() || null,
	}
}
