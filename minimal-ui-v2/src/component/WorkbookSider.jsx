import { Icon } from '@iconify/react';
import { Menu } from 'antd';
import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';


const siderStyle = {
    border:0,
    backgroundColor: "#1c1c1c",
    
}

function WorkbookSider() {
    const [selectedMenuKey, setSelectedMenuKey] = useState(["1"])
    const location = useLocation()
    const navigate = useNavigate()

    useEffect(() => {
        const pathname = location.pathname.split("/").pop()

        if (pathname === "dashboard") {
            setSelectedMenuKey(["1"])
        } else if (pathname === "edit") {
            setSelectedMenuKey(["2"])
        }
        else if (pathname === "runs") {
        setSelectedMenuKey(["3"])
        }
        else if (pathname === "scheduler") {
        setSelectedMenuKey(["4"])
        }
        else {
            setSelectedMenuKey(["5"])
        }
    }, [location])

    function navigateWorkbook(e) {
        setSelectedMenuKey(e.key)
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
            navigate("schedules")
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
            label: "dashboard",
            icon: <Icon icon="carbon:dashboard" color="white" />,
            style: {
                border: "solid #2d2d2d 1px"
            }
        },
        {
            key: "2",
            label: "edit",
            icon: <Icon icon="ant-design:edit-outlined" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }
        },
        {
            key: "3",
            label: "runs",
            icon: <Icon icon="fluent-mdl2:trigger-auto" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }
        },
        {
            key: "4",
            label: "schedules",
            icon: <Icon icon="carbon:event-schedule" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }
        },
        {
            key: "5",
            label: "settings",
            icon: <Icon icon="fluent:settings-20-regular" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }
        }
    ]
    
  return (
      <Menu 
        mode="inline" 
        defaultSelectedKeys={["2"]}
        selectedKeys={selectedMenuKey}
        items={items}
        style={siderStyle}
        onClick={(e) => {navigateWorkbook(e)}}
      />
  )
}

export default WorkbookSider
