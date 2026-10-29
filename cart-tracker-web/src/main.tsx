import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Стили Leaflet: без них тайлы карты разъезжаются и маркеры рисуются не на месте.
import 'leaflet/dist/leaflet.css'
import App from './app/App'

const rootElement = document.getElementById('root')
if (!rootElement) {
	throw new Error('В index.html нет элемента <div id="root">')
}

// </StrictMode><StrictMode> — режим строгой проверки, работает только при разработке. Он нарочно запускает часть кода дважды, чтобы найти ошибки, например незакрытые таймеры и подключения. В готовой сборке он ничего не делает. Это важно запомнить для шага 5: если данные загружаются два раза, значит, не написана функция очистки в useEffect.

createRoot(rootElement).render(
	<StrictMode>
		<App />
	</StrictMode>,
)
