import { AppBar, Box, Typography, IconButton, Stack } from '@mui/material'
import propTypes from 'prop-types'
import SinkConfig from '../../components/AppSideBar/SinkConfig'
import SourceConfig from '../../components/AppSideBar/SourceConfig'
import TransformConfig from '../../components/AppSideBar/TransformConfig'
import { getTitleForSidebar } from "../../utils/ui.util";
import Close from '@mui/icons-material/Close';

AppSidebar.propTypes = {
    currNode: propTypes.object,
    closeBar: propTypes.func
}

function AppSidebar({ currNode, closeBar }) {
    return (
        <Box sx={{ minWidth: 550 }} role="presentation">
            <AppBar position='static' sx={{ height: 64 }} style={{
                justifyContent: "center",
                padding: '0 16px'
            }}>
                <Stack direction={"row"} justifyContent={"space-around"} alignItems={"center"}>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Configure {getTitleForSidebar(currNode.data.type)}
                    </Typography>
                    <IconButton aria-label="Close" onClick={closeBar}>
                        <Close style={{
                            color: 'white'
                        }} />
                    </IconButton>
                </Stack>
            </AppBar>
            <Box padding={2} sx={{ overflowY: 'auto', maxHeight: 'calc(100vh - 64px)', padding: 2, overflow: 'hidden' }}>
                {currNode.data.type === 'input' && <SourceConfig closeBar={closeBar} currNode={currNode} />}
                {currNode.data.type === 'default' && <TransformConfig closeBar={closeBar} currNode={currNode} />}
                {currNode.data.type === 'output' && <SinkConfig closeBar={closeBar} currNode={currNode} />}
            </Box>
        </Box>
    )
}

export default AppSidebar

