import Router from './routes'
import ThemeProvider from "./theme"
import ScrollToTop from './components/ScrollToTop'
import "@fontsource/lato"; // Defaults to weight 400
import "@fontsource/lato/400.css"; // Specify weight
import "@fontsource/lato/400-italic.css"; // Specify weight and style

function App() {

  return (
    <ThemeProvider>
      <ScrollToTop/>
      <Router/>
    </ThemeProvider>
    
  )
}

export default App
