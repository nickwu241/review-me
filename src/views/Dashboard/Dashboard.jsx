import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';

import ReviewMeAPI from '../../ReviewMeAPI'
import Store from '../../Store'

import Button from 'material-ui/Button'
import IconButton from 'material-ui/IconButton';
import Switch from 'material-ui/Switch'
import Input from 'material-ui/Input'
import DeleteIcon from 'material-ui-icons/Delete'
import List, {
    ListItem,
    ListItemSecondaryAction,
} from 'material-ui/List'

class Dashboard extends Component {
    constructor(props) {
        super(props)
        this.NOTIFCATION_TICK_MS = 3000
        this.MS_PER_S = 1000
        this.API = new ReviewMeAPI()
        this.state = {
            refreshRate: Store.refreshRate,
            checkReviews: Store.checkReviews,
            checkNotifications: Store.checkNotifications,
            inputRepo: Store.inputRepo,
            reposTracking: Store.reposTracking
        }
    }
    tick = () => {
        if (!this.state.checkReviews) {
            return
        }
        this.API.should_notify()
    }
    notifcationTick = () => {
        if (!this.state.checkNotifications) {
            return
        }
        this.API.notifications()
    }
    handleRefreshRate = e => {
        let rate = parseInt(e.target.value, 10)
        this.setState({ refreshRate: rate })
        clearInterval(this.tickTimer)
        if (!this.state.refreshRate) {
            return
        }
        let ms = rate * this.MS_PER_S
        this.tickTimer = setInterval(this.tick, ms)
    }
    handleReviews = (e, checked) => this.setState({ checkReviews: checked })
    handleNotifications = (e, checked) => this.setState({ checkNotifications: checked })
    handleInputRepo = (e) => this.setState({ inputRepo: e.target.value })
    handleTrack = (e) => {
        this.setState(prev => ({
            reposTracking: [...prev.reposTracking, this.state.inputRepo],
            inputRepo: ''
        }))
    }
    handleInputRepoKeyPress = (e) => {
        if (e.key === 'Enter') {
            this.setState(prev => ({
                reposTracking: [...prev.reposTracking, this.state.inputRepo],
                inputRepo: ''
            }))
        }
    }
    handleDeleteRepo = (repo) => {
        let i = this.state.reposTracking.indexOf(repo)
        let arr = this.state.reposTracking
        arr.splice(i, 1)
        this.setState({ reposTracking: arr })
    }
    componentDidMount() {
        let ms = this.state.refreshRate * this.MS_PER_S
        this.tickTimer = setInterval(this.tick, ms)
        this.notificationTickTimer = setInterval(this.notifcationTick, this.NOTIFCATION_TICK_MS)
    }
    componentWillUnmount() {
        // Store our state
        for (let item in this.state) {
            Store[item] = this.state[item]
        }
        // Clean up our timers
        clearInterval(this.tickTimer)
        clearInterval(this.notificationTickTimer)
    }
    render() {
        return (
            <div className="content">
                <Grid fluid>
                    <Col md={6}>
                        <Row>
                            <h2>Notifications</h2>
                            <Switch onChange={this.handleReviews} checked={this.state.checkReviews} /> Automatically Request for Reviews
                            || Request Rate:
                                <Input type="number"
                                placeholder="Rate"
                                style={{ marginLeft: '8px', fontSize: '1em', width: '40px' }}
                                value={this.state.refreshRate}
                                onChange={this.handleRefreshRate} />s
                        </Row>
                        <Row>
                            <Switch onChange={this.handleNotifications} checked={this.state.checkNotifications} />
                            Send Slack Notifications for unread Github Notifications
                        </Row>
                    </Col>
                    <Col md={6}>
                        <Row>
                            <h2>Repositories Tracking</h2>
                            <Col md={6}>
                                <List>
                                    {this.state.reposTracking.map((repo, key) => {
                                        return (
                                            <ListItem key={key}>
                                                {repo}
                                                <ListItemSecondaryAction onClick={this.handleDeleteRepo}>
                                                    <IconButton aria-label="Delete">
                                                        <DeleteIcon />
                                                    </IconButton>
                                                </ListItemSecondaryAction>
                                            </ListItem>
                                        )
                                    })}
                                </List>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={5}>
                                <Input
                                    type="text"
                                    placeholder="Repository Name"
                                    style={{ fontSize: '1em' }}
                                    fullWidth={true}
                                    onKeyPress={this.handleInputRepoKeyPress}
                                    onChange={this.handleInputRepo}
                                    value={this.state.inputRepo} />
                            </Col>
                            <Col md={1}>
                                <Button
                                    variant="raised"
                                    color="secondary"
                                    onClick={this.handleTrack}>
                                    Track
                                </Button>
                            </Col>
                        </Row>
                    </Col>
                </Grid>
            </div>
        );
    }
}

export default Dashboard;
