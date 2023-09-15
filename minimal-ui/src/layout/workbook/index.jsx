import { styled } from "@mui/material/styles";
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { backendApi } from "../../api/api";
import { pipelineStore } from "../../appState/pipelineStore";
import PIPELINE_DATA from "../../mock/PIPELINE_DATA.json";
import { getUuidFrpmPath } from "../../utils/formatString";
import Navbar from "../navBar";
import AppFlow from "./appFlow";


const TOP_PADDING = 64;


const RootStyle = styled('div')({
  display: 'flex',
  height: '100vh',
  overflow: 'hidden'
});

const MainStyle = styled('div')(({ theme }) => ({
  flexGrow: 1,
  height: '95vh',
  [theme.breakpoints.up('lg')]: {
    paddingTop: TOP_PADDING,
  }
}));



export default function WorkBook() {

  const [pipeline, { setPipeline }] = pipelineStore()
  let locState = useLocation()

  useEffect(() => {

    async function getPipeline(pipelineUuid) {
      const response = await backendApi.get(`/pipeline/${pipelineUuid}`).catch(() => {
        return { data: { pipeline: PIPELINE_DATA } };
      })

      if (response.data) {
        setPipeline(response.data.pipeline)
      }
    }

    const pipelineUuid = getUuidFrpmPath(locState.pathname)
    getPipeline(pipelineUuid)

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  
  return (
    <RootStyle>
      <Navbar title={pipeline.pipeline.name}/>
      <MainStyle >
        <AppFlow />
      </MainStyle>
    </RootStyle>
  )

}
