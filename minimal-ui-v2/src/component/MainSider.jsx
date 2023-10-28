import { Icon } from '@iconify/react';
import { Menu } from 'antd';
import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';


const siderStyle = {
    border: 0,
    backgroundColor: "#1c1c1c"
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
            icon: <Icon icon="carbon:dashboard" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }

        },
        {
            key: "2",
            label: "Pipeline List",
            icon: <Icon icon="ion:list-outline" color="white" />,
            style: {
                border: "solid #2d2d2d 1px",
                marginTop: "1rem"
            }
        }
    ]
    return (
        <Menu
            mode="inline"
            defaultSelectedKeys={["1"]}
            selectedKeys={selectedMenuKey}
            items={items}
            onClick={(e) => { navigateDashboard(e) }}
            style={siderStyle}
            />
    )
}

export default MainSider
