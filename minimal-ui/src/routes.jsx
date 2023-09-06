import { useRoutes } from "react-router-dom";
import Home from "./layout/home";
import Dashboard from "./layout/dashboard";
import WorkBook from "./layout/workbook";


export default function Router() {
  return useRoutes([
    { 
      path: "/", 
      element: <Home />,
      children: [
        {
          path: "/",
          element: <Dashboard/>
        },
        
      ]
    },
    {
      path: "app/:pipelineUUID",
      element: <WorkBook/>
    }]);
}
