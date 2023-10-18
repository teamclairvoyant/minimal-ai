import { Breadcrumb, Layout, Menu, theme  } from 'antd';
import { Outlet } from "react-router-dom";
import MainHeader from '../../component/MainHeader';
import MainSider from '../../component/MainSider';

const { Header,Content, Sider } = Layout;

const siderStyle = {
    backgroundColor: '#141414',
    top: 0,
    left: 0,
}

const contentStyle = {
    color: '#fff',
    marginRight: "1rem",
    marginLeft: "1rem",
    display: "flex",
    flexDirection: "column",
}

const headerStyle = {
    backgroundColor: '#141414',
    height: "3rem",
    position: "sticky",
    top: 0,
    zIndex: 1,
    paddingLeft: "1rem",
    paddingRight: "0.5rem"
}
  

function Home() {
    
    return (
        <Layout style={{height: "100vh"}}>
            <Header style={headerStyle}>
                <MainHeader/>
            </Header>
            <Layout>
                <Sider width={"4rem"} style={siderStyle}>
                    <MainSider/>
                </Sider>
                <Layout>
                    <Content style={contentStyle}>
                        <Outlet/>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

export default Home
