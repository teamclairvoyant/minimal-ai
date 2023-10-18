import { useEffect } from 'react';
import { Layout } from 'antd';
import { Outlet, useLocation } from "react-router-dom";
import MainHeader from '../../component/MainHeader';
import WorkbookSider from '../../component/WorkbookSider';
import { pipelineStore } from '../../appState/pipelineStore'
import { backendApi } from '../../api/api';
import { getUuidFromPath } from "../../utils/formatString";


const { Content, Sider } = Layout;

const siderStyle = {
    position: 'fixed',
    height: "100vh",
    backgroundColor: '#202020',
    overflow: "auto",
    top: 0,
    left: 0,
    bottom: 0
};

const contentStyle = {
    color: '#fff',
    marginTop: "10px",
    marginRight: "15px",
    marginLeft: "60px",
    overflow: "initial"
};
  

function Workbook() {
  const [, { setPipeline }] = pipelineStore()
  let locState = useLocation()

  useEffect(() => {

    async function getPipeline(pipelineUuid) {
      try {
      const response = await backendApi.get(`/pipeline/${pipelineUuid}`)

      if (response.data) {
        setPipeline(response.data.pipeline)
      }
    }
    catch(error){
      console.log(error)
    }
    }
    const pipelineUuid = getUuidFromPath(locState.pathname)

    getPipeline(pipelineUuid)

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <Layout>
        <Sider width="60px" style={siderStyle}>
            <WorkbookSider/>
        </Sider>
        <Layout>
            <Content style={contentStyle}>
                <MainHeader/>
                <Outlet/>
            </Content>
        </Layout>
    </Layout>
  )
}

export default Workbook
