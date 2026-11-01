// Выбор источника по адресу страницы.
//
// По умолчанию играем запись (демо работает без сервера). Живой режим
// включается явно: /?source=live — тогда раз в секунду опрашивается
// /data/live-scenario.json, который пишет внешний процесс.

export type SourceMode = 'replay' | 'live'

export function sourceModeFromUrl(search: string): SourceMode {
	const mode = new URLSearchParams(search).get('source')
	return mode === 'live' ? 'live' : 'replay'
}
