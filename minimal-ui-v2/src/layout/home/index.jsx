import { Layout } from 'antd';
import { Outlet } from "react-router-dom";
import MainHeader from '../../component/MainHeader';
import MainSider from '../../component/MainSider';
import { useState } from 'react';

const { Header,Content, Sider } = Layout;

const headerStyle = {
    backgroundColor: '#141414',
    position: "sticky",
    top: 0,
    zIndex: 1,
    paddingLeft: "1.5rem"
}
  

function Home() {
    const [collapsed, setCollapsed] = useState(true);

    return (
        <Layout>
            <Header style={headerStyle}>
                <MainHeader/>
            </Header>
            <Layout style={{ minHeight: `calc(100vh - 64px)`}}>
                <Sider collapsed={collapsed} 
                    onMouseEnter={() => setCollapsed(false)} 
                    onMouseLeave={() => setCollapsed(true)} 
                    style={{backgroundColor: "#141414"}}>
                    <MainSider />
                </Sider>
                <Layout style={{padding: "0 2rem 2rem 2rem"}}>
                    <Content>
                        <Outlet/>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    )
}

export default Home
