import { Icon } from '@iconify/react';
import { Menu } from 'antd';
import { useNavigate } from 'react-router-dom';

const siderStyle = {
    backgroundColor:"inherit",
    border:0,
    height: "300px",
    display: "flex",
    flexDirection: "column",
    paddingTop: 40
}

function MainSider() {

    const navigate = useNavigate()

    function navigateDashboard(e) {

        if (e.key == 1){
            navigate("/")
        }
        else if (e.key == 2){
            navigate("/pipelines")
        }
        else{
            console.log("not implemented")
        }
        
    }

    const items = [
        {
            key: "1",
            icon: <Icon icon="carbon:dashboard" color="white" height={30} width={30} />,
            style: {
                paddingLeft:10
            }
        },
        {
            key: "2",
            icon: <Icon icon="cil:list" color="white" height={30} width={30} />,
            style: {
                paddingLeft:10
            }
        }
    ]
  return (
    <div style={{paddingTop:"10px"}}>
      <Menu mode="inline" defaultSelectedKeys={['1']} items={items} style={siderStyle} onClick={(e) => {navigateDashboard(e)}}/>
    </div>
  )
}

export default MainSider
