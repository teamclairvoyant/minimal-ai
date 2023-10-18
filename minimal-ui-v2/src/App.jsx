import Router from './routes'
import {ConfigProvider, theme} from 'antd'

function App() {
  return (
    <ConfigProvider
    theme={{
      algorithm: theme.darkAlgorithm,

    }}
    >
      <Router/>
    </ConfigProvider>
    
  )
}

export default App
