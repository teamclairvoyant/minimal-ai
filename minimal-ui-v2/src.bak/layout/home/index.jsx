import { Layout } from 'antd';
import { Outlet } from "react-router-dom";
import MainHeader from '../../component/MainHeader';
import MainSider from '../../component/MainSider';

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
  

function Home() {
  return (
    <Layout>
        <Sider width="60px" style={siderStyle}>
            <MainSider/>
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

export default Home
