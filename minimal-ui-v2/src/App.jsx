import { ConfigProvider, message, theme } from "antd";
import Router from "./routes";

function App() {
  const [, contextHolder] = message.useMessage();
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
      }}
    >
      {contextHolder}
      <Router />
    </ConfigProvider>
  );
}

export default App;
