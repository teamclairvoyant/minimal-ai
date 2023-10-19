import { Menu } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { AreaChartOutlined, UnorderedListOutlined } from '@ant-design/icons'

import { useEffect, useState } from 'react';


const siderStyle = {
    border: 0
}

function MainSider() {
    const [selectedMenuKey, setSelectedMenuKey] = useState(["1"]);
    const location = useLocation();

    useEffect(() => {
        if (location.pathname === "/pipelines") {
            setSelectedMenuKey(["2"]);
        } else {
            setSelectedMenuKey(["1"]);
        }
    }, [location]);

    const navigate = useNavigate()

    function navigateDashboard(e) {
        setSelectedMenuKey(e.key);
        if (e.key == "1") {
            navigate("/")
        }
        else if (e.key == "2") {
            navigate("/pipelines")
        }
        else {
            console.log("not implemented")
        }
    }

    const items = [
        {
            key: "1",
            label: "Dashboard",
            icon: <AreaChartOutlined />,

        },
        {
            key: "2",
            label: "Pipeline List",
            icon: <UnorderedListOutlined />,
        }
    ]
    return (
        <Menu
            mode="inline"
            defaultSelectedKeys={["1"]}
            selectedKeys={selectedMenuKey}
            items={items}
            onClick={(e) => { navigateDashboard(e) }}
            style={siderStyle} />
    )
}

export default MainSider
