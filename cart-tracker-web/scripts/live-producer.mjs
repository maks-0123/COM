#!/usr/bin/env node
// «Продюсер» для живого режима: раз в секунду пишет public/data/live-scenario.json.
//
// Запускать параллельно с `npm run dev`, открывать /?source=live.
// Файл заменяется атомарно (tmp + rename), чтобы браузер никогда не прочитал
// половину JSON. Данные синтетические: тележки едут по кругу площадки.

import { readFile, rename, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(dirname(fileURLToPath(import.meta.url)))
const demoPath = join(root, 'public/data/demo-scenario.json')
const livePath = join(root, 'public/data/live-scenario.json')

const demo = JSON.parse(await readFile(demoPath, 'utf8'))

// Стартуем с первых отметок демо, чтобы тележки не прыгали в начало координат.
const start = new Map()
for (const fix of demo.fixes) if (!start.has(fix.cartId)) start.set(fix.cartId, fix.position)

const points = new Map(
	demo.carts.map((cart) => [cart.id, { ...(start.get(cart.id) ?? { x: 0, y: 0 }) }]),
)
const fixes = []

function step() {
	const ts = new Date().toISOString()

	for (const [cartId, point] of points) {
		point.x = (point.x + 1.7) % 180
		point.y = (point.y + 0.9) % 140
		fixes.push({
			cartId,
			ts,
			position: { x: Math.round(point.x), y: Math.round(point.y) },
			accuracyM: 15,
			method: 'rssi-multilateration',
		})
	}

	// Храним только последние 200 отметок, чтобы файл не рос бесконечно.
	while (fixes.length > 200) fixes.shift()

	const snapshot = { ...demo, generatedAt: ts, fixes }
	const tmp = `${livePath}.tmp`
	writeFile(tmp, JSON.stringify(snapshot, null, '\t'))
		.then(() => rename(tmp, livePath))
		.catch((error) => console.error('не удалось записать снимок:', error.message))
}

step()
setInterval(step, 1000)
console.log(`Пишу ${livePath} раз в секунду. Открой /?source=live на dev-сервере.`)
