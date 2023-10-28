import { Layout } from 'antd';
import { Outlet } from "react-router-dom";
import MainHeader from '../../component/MainHeader';
import MainSider from '../../component/MainSider';

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

    return (
        <Layout>
            <Header style={headerStyle}>
                <MainHeader/>
            </Header>
            <Layout>
                <Sider collapsed
                    style={siderStyle}
                    collapsedWidth={60}>
                    <MainSider />
                </Sider>
                <Layout style={{padding: "0 1rem 2rem 5rem", backgroundColor: "#1c1c1c"}}>
                    <Content>
                        <Outlet/>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

export default Home
