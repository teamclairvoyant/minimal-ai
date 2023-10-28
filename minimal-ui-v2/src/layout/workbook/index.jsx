import { Layout } from 'antd';
import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { backendApi } from '../../api/api';
import { pipelineStore } from '../../appState/pipelineStore';
import MainHeader from '../../component/MainHeader';
import WorkbookSider from '../../component/WorkbookSider';
import { getUuidFromPath } from '../../utils/formatString';


const { Header,Content, Sider } = Layout;

const headerStyle = {
    backgroundColor: '#1c1c1c',
    position: "sticky",
    top: 0,
    zIndex: 1,
    padding: "0 1rem 0 1rem",
    borderBottom: "solid black 1px"
}

const siderStyle = {
    backgroundColor: '#1c1c1c',
    overflow: 'auto',
    height: '100vh',
    position: 'fixed',
    width: "4rem",
    paddingTop: "1rem",
    borderRight: "solid black 1px"
}

function Home() {
    const [, {setPipeline}] = pipelineStore()
    let locState = useLocation()
    useEffect(() => {

        async function getPipeline(pipelineUuid) {
          const response = await backendApi.get(`/pipeline/${pipelineUuid}`)
    
          if (response.data) {
            setPipeline(response.data.pipeline)
          }
        }
    
        const pipelineUuid = getUuidFromPath(locState.pathname)
        getPipeline(pipelineUuid)
    
      }, [])

    return (
        <Layout>
            <Header style={headerStyle}>
                <MainHeader/>
            </Header>
            <Layout>
                <Sider collapsed
                    style={siderStyle}
                    collapsedWidth={60}>
                    <WorkbookSider />
                </Sider>
                <Layout style={{padding: "0 0 2rem 4rem", backgroundColor: "#1c1c1c"}}>
                    <Content>
                        <Outlet/>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

export default Home
