import { useRoutes } from "react-router-dom";
import Home from "./layout/home";
import Dashboard from "./layout/dashboard";
import WorkBook from "./layout/workbook";
import PipelineList from "./layout/pipelineList";
import PipelineDashboard from "./component/Workbook/Dashboard";
import EditWorkbook from "./component/Workbook/EditWorkbook";
import PipelineRuns from "./component/Workbook/PipelineRuns";
import PipelineScheduler from "./component/Workbook/PipelineScheduler";
import PipelineSettings from "./component/Workbook/PipelineSettings";


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
      ]
    },
    {
      path: "pipeline/:pipelineUUID",
      element: <WorkBook/>,
      children: [
        {
          path: "/pipeline/:pipelineUUID/dashboard",
          element: <PipelineDashboard/>
        },
        {
          path: "/pipeline/:pipelineUUID/edit",
          element: <EditWorkbook/>
        },
        {
          path: "/pipeline/:pipelineUUID/runs",
          element: <PipelineRuns/>
        },
        {
          path: "/pipeline/:pipelineUUID/scheduler",
          element: <PipelineScheduler/>
        },
        {
          path: "/pipeline/:pipelineUUID/settings",
          element: <PipelineSettings/>
        }
      ]
    }
    ]);
}
