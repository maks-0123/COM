import { useEffect, useMemo, useState } from 'react'
import { countStale } from '../domain/status'
import type { PositionFix, ScenarioFile } from '../domain/types'
import { MapView } from '../features/map/MapView'
import { FileReplaySource } from '../sources/file/FileReplaySource'
import { createReplayClock } from '../sources/file/ReplayClock'
import { parseJsonScenario } from '../sources/file/parsers/parseJsonScenario'

// Демо-сценарий проигрывается по записанным отметкам: тележки двигаются,
// а не стоят на первой точке. Источник и часы — сменные части, карта о них
// ничего не знает (см. sources/PositionSource.ts).

const SCENARIO_URL = '/data/demo-scenario.json'
const REPLAY_SPEED = 1

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

	return (
		// Leaflet нужна явная высота контейнера, иначе карта будет высотой 0 px.
		// position: fixed + inset: 0 растягивает блок на всё окно браузера.
		<div style={{ position: 'fixed', inset: 0 }}>
			<Replay scenario={state.scenario} />
		</div>
	)
}

/** Проигрывает сценарий и отдаёт карте текущую отметку каждой тележки. */
function Replay({ scenario }: { scenario: ScenarioFile }) {
	const [positions, setPositions] = useState<Map<string, PositionFix>>(() => new Map())
	const [nowMs, setNowMs] = useState<number | null>(null)

	const { site, stations, carts } = scenario
	const { startMs, endMs } = useMemo(() => timeRange(scenario), [scenario])

	// Сколько тележек давно не присылали координат: по этому числу
	// показываем предупреждение, а сами точки гасит CartLayer.
	const staleCount = useMemo(
		() => (nowMs === null ? 0 : countStale(positions.values(), nowMs)),
		[positions, nowMs],
	)

	useEffect(() => {
		const clock = createReplayClock({ speed: REPLAY_SPEED })
		const source = new FileReplaySource(scenario, clock, { loop: true })

		const offFix = source.onFix((fix) => {
			setPositions((prev) => {
				const next = new Map(prev)
				next.set(fix.cartId, fix)
				return next
			})
		})
		const offReset = source.onReset(() => setPositions(new Map()))
		const offTick = clock.onTick((now) => setNowMs(now))

		source.start()

		return () => {
			offFix()
			offReset()
			offTick()
			source.stop()
		}
	}, [scenario])

	return (
		<>
			<MapView
				site={site}
				stations={stations}
				carts={carts}
				positions={positions}
				nowMs={nowMs ?? startMs}
			/>
			<ReplayStatus
				nowMs={nowMs}
				startMs={startMs}
				endMs={endMs}
				staleCount={staleCount}
				totalCount={positions.size}
			/>
		</>
	)
}

/** Границы записи в миллисекундах: по ним считается прогресс воспроизведения. */
function timeRange(scenario: ScenarioFile): { startMs: number; endMs: number } {
	if (scenario.fixes.length === 0) return { startMs: 0, endMs: 0 }

	let startMs = Number.POSITIVE_INFINITY
	let endMs = Number.NEGATIVE_INFINITY
	for (const fix of scenario.fixes) {
		const ts = Date.parse(fix.ts)
		if (ts < startMs) startMs = ts
		if (ts > endMs) endMs = ts
	}
	return { startMs, endMs }
}

type StatusProps = {
	nowMs: number | null
	startMs: number
	endMs: number
	staleCount: number
	totalCount: number
}

/** Небольшая плашка с прогрессом записи и предупреждением об устаревании. */
function ReplayStatus({ nowMs, startMs, endMs, staleCount, totalCount }: StatusProps) {
	const elapsed = nowMs === null ? 0 : Math.max(0, nowMs - startMs) / 1000
	const total = Math.max(0, endMs - startMs) / 1000

	return (
		<div
			style={{
				position: 'absolute',
				left: 12,
				bottom: 12,
				zIndex: 1000,
				padding: '6px 10px',
				border: `1px solid ${staleCount > 0 ? '#f59e0b' : '#cbd5e1'}`,
				borderRadius: 8,
				background: 'rgba(255, 255, 255, 0.92)',
				color: '#0f172a',
				font: '13px/1.4 system-ui, sans-serif',
			}}
		>
			<div>
				Запись: {elapsed.toFixed(1)} / {total.toFixed(1)} с · ×{REPLAY_SPEED}
			</div>
			{staleCount > 0 && (
				<div style={{ color: '#b45309' }}>
					Устарело: {staleCount} из {totalCount}
				</div>
			)}
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
