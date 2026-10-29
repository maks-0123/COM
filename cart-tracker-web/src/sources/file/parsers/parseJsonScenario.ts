import type { z } from 'zod'
import { ScenarioSchema } from '../../../domain/schemas'
import type { ScenarioFile } from '../../../domain/types'

// Текст файла -> проверенный сценарий или список понятных ошибок.
// Функция никогда не бросает исключение: плохой файл — это нормальная
// ситуация, интерфейс должен показать ошибки, а не упасть.

export type ParseResult =
	| { ok: true; scenario: ScenarioFile }
	| { ok: false; errors: string[] }

export function parseJsonScenario(text: string): ParseResult {
	let raw: unknown
	try {
		raw = JSON.parse(text)
	} catch (e) {
		return { ok: false, errors: [`Файл не является JSON: ${(e as Error).message}`] }
	}

	const result = ScenarioSchema.safeParse(raw)
	if (!result.success) {
		return { ok: false, errors: result.error.issues.map(formatIssue) }
	}

	// Отметки в файле могут идти в любом порядке — упорядочиваем по времени.
	const scenario = result.data
	const fixes = [...scenario.fixes].sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts))
	return { ok: true, scenario: { ...scenario, fixes } }
}

/** ['fixes', 3, 'position'] -> "fixes[3].position: <сообщение>" */
function formatIssue(issue: z.core.$ZodIssue): string {
	const path = issue.path
		.map((part, i) => (typeof part === 'number' ? `[${part}]` : i === 0 ? String(part) : `.${String(part)}`))
		.join('')
	return path ? `${path}: ${issue.message}` : issue.message
}
