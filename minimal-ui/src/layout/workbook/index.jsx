import { useLocation } from "react-router-dom";
import { styled } from "@mui/material/styles";
import Navbar from "../navBar";
import AppFlow from "./appFlow";
import { getUuidFrpmPath } from "../../utils/formatString";
import { useEffect } from "react";
import { backendApi } from "../../api/api";
import { pipelineStore } from "../../appState/pipelineStore";


const TOP_PADDING = 64;


const RootStyle = styled('div')({
    display: 'flex',
    minHeight: '100%',
    overflow: 'hidden'
});

const MainStyle = styled('div')(({ theme }) => ({
    flexGrow: 1,
    overflow: 'auto',
    minHeight: '100%',
    paddingTop: TOP_PADDING,
    paddingBottom: theme.spacing(10),
    [theme.breakpoints.up('lg')]: {
        paddingTop: TOP_PADDING,
        
    }
}));



export default function WorkBook() {

  const [ , {setPipeline}] = pipelineStore()
  let  locState  = useLocation()
  
  useEffect(() => {

    async function getPipeline(pipelineUuid){
      const response = await backendApi.get(`/api/v1/pipeline/${pipelineUuid}`)
      
      if (response.data){
        setPipeline(response.data.pipeline)
      }
    }

    const pipelineUuid = getUuidFrpmPath(locState.pathname)
    getPipeline(pipelineUuid)
    
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[])

    return (
      <RootStyle>
        <Navbar />
          <MainStyle>
            <AppFlow ></AppFlow>
          </MainStyle>
      </RootStyle>
    )

}
