import {Flex, Col, Avatar, Badge, Popover} from 'antd'
import { Link as RouterLink } from 'react-router-dom';
import { BellOutlined, UserOutlined } from '@ant-design/icons';
import logo from '../assets/images/EXL_Service_logo.png'


function MainHeader() {

  const notification = (
    <div>
      <p>Content</p>
      <p>Content</p>
    </div>
  )

  const userSettings = (
    <div>
      <p>Settings</p>
      <p>Logout</p>
    </div>
  )



  return (
    <Flex gap="middle" align='center' justify='space-between'>
      <Col>
        <RouterLink to="/">
          <img
              width={40}
              src={logo}
            />
        </RouterLink>
        
      </Col>
      <Flex gap="middle">
        <Col>
          <Popover content={notification} title="New Notification">
              <Badge count={0} offset={[5,2]}>
                <Avatar icon={<BellOutlined />}/>
              </Badge>
          </Popover>
        </Col>
        <Col >
          <Popover content={userSettings}>
            <Avatar style={{ backgroundColor: '#db553d' }} icon={<UserOutlined />} />
          </Popover>
        </Col>
      </Flex>
    </Flex>
  )
}

export default MainHeader
