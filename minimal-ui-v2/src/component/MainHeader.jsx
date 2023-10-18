import {Row, Col, Avatar, Badge, Popover} from 'antd'
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
    <Row style={{paddingLeft: "24px", justifyContent: "space-between"}}>
      <Col style={{paddingTop: 10}}>
        <RouterLink to="/">
          <img
              width={40}
              height={20}
              src= {logo}
            />
        </RouterLink>
        
      </Col>
      <Row gutter={30}>
        <Col style={{paddingTop: 10}}>
          <Popover content={notification} title="New Notification">
              <Badge count={0} offset={[5,2]}>
                <Avatar icon={<BellOutlined />}/>
              </Badge>
          </Popover>
        </Col>
        <Col style={{paddingTop: 10}}>
          <Popover content={userSettings}>
            <Avatar style={{ backgroundColor: '#db553d' }} icon={<UserOutlined />} />
          </Popover>
        </Col>
      </Row>
    </Row>
  )
}

export default MainHeader
