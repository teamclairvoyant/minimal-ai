import { Icon } from '@iconify/react';
import { Menu } from 'antd';
import { useNavigate } from 'react-router-dom';

const siderStyle = {
    border:0,
    paddingTop: "1rem"
}

function WorkbookSider() {
    const navigate = useNavigate()

    function navigateWorkbook(e) {

        if (e.key == 1){
            navigate("dashboard")
        }
        else if (e.key == 2){
            navigate("edit")
        }
        else if(e.key == 3){
            navigate("runs")
        }
        else if(e.key == 4){
            navigate("scheduler")
        }
        else if(e.key == 5){
            navigate("settings")
        }
        else {
            console.log("not implemented")
        }
        
    }

    const items = [
        {
            key: "1",
            id: "dashboard",
            icon: <Icon icon="carbon:dashboard" color="white" height={30} width={30} />,
            style: {
                paddingLeft:"0.8rem"
            }
        },
        {
            key: "2",
            id: "edit",
            icon: <Icon icon="ant-design:edit-outlined" color="white" height={30} width={30} />,
            style: {
                paddingLeft:"0.8rem"
            }
        },
        {
            key: "3",
            id: "triggers",
            icon: <Icon icon="fluent-mdl2:trigger-auto" color="white" height={30} width={30} />,
            style: {
                paddingLeft:"0.8rem"
            }
        },
        {
            key: "4",
            id: "schedules",
            icon: <Icon icon="carbon:event-schedule" color="white" height={30} width={30} />,
            style: {
                paddingLeft:"0.8rem"
            }
        },
        {
            key: "5",
            id: "settings",
            icon: <Icon icon="fluent:settings-20-regular" color="white" height={30} width={30} />,
            style: {
                paddingLeft:"0.8rem"
            }
        }
    ]
    
  return (
    <div>
      <Menu mode="inline" defaultSelectedKeys={["2"]} items={items} style={siderStyle} onClick={(e) => {navigateWorkbook(e)}}/>
    </div>
  )
}

export default WorkbookSider
