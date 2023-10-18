import { useRoutes } from "react-router-dom";
import Home from "./layout/home";
import Dashboard from "./layout/dashboard";
import WorkBook from "./layout/workbook";
import PipelineList from "./layout/pipelineList";

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
        {
          path: "/pipelines",
          element: <PipelineList/>
        },
        {
          path: "app/:pipelineUUID",
          element: <WorkBook/>
        }
        
      ]
    }
    ]);
}
