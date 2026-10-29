import { useEffect, useState } from 'react'
import type { PositionFix, ScenarioFile } from '../domain/types'
import { MapView } from '../features/map/MapView'
import { parseJsonScenario } from '../sources/file/parsers/parseJsonScenario'

// ВРЕМЕННО: файл загружается прямо в App, тележки стоят на первой отметке.
// Дальше загрузка переедет в FileReplaySource (проигрывание во времени).
const SCENARIO_URL = '/data/demo-scenario.json'

type LoadState =
	| { status: 'loading' }
	| { status: 'error'; errors: string[] }
	| { status: 'ready'; scenario: ScenarioFile }

export default function App() {
	const state = useScenario(SCENARIO_URL)

	if (state.status === 'loading') {
		return <p style={{ padding: 16 }}>Загрузка {SCENARIO_URL}…</p>
	}
	if (state.status === 'error') {
		return (
			<div style={{ padding: 16 }}>
				<h3>Не удалось открыть {SCENARIO_URL}</h3>
				<ul>
					{state.errors.map((e) => (
						<li key={e}>{e}</li>
					))}
				</ul>
			</div>
		)
	}

	const { site, stations, carts, fixes } = state.scenario

	return (
		// Leaflet нужна явная высота контейнера, иначе карта будет высотой 0 px.
		// position: fixed + inset: 0 растягивает блок на всё окно браузера.
		<div style={{ position: 'fixed', inset: 0 }}>
			<MapView
				site={site}
				stations={stations}
				carts={carts}
				positions={firstFixPerCart(fixes)}
			/>
		</div>
	)
}

/** Скачивает и проверяет файл сценария. */
function useScenario(url: string): LoadState {
	const [state, setState] = useState<LoadState>({ status: 'loading' })

	useEffect(() => {
		// AbortController отменяет загрузку, если компонент убрали со страницы
		// раньше, чем пришёл ответ (StrictMode так делает при разработке).
		const controller = new AbortController()

		fetch(url, { signal: controller.signal })
			.then((response) => {
				if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
				return response.text()
			})
			.then((text) => {
				const result = parseJsonScenario(text)
				setState(
					result.ok
						? { status: 'ready', scenario: result.scenario }
						: { status: 'error', errors: result.errors },
				)
			})
			.catch((e: Error) => {
				if (e.name !== 'AbortError') setState({ status: 'error', errors: [e.message] })
			})

		return () => controller.abort()
	}, [url])

	return state
}

/** Первая по времени отметка каждой тележки (fixes уже упорядочены по ts). */
function firstFixPerCart(fixes: PositionFix[]): Map<string, PositionFix> {
	const result = new Map<string, PositionFix>()
	for (const fix of fixes) {
		if (!result.has(fix.cartId)) result.set(fix.cartId, fix)
	}
	return result
}
