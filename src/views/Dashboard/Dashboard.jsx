import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';

import ReviewMeAPI from '../../ReviewMeAPI'

import Switch from 'material-ui/Switch'
import Input from 'material-ui/Input'

class Dashboard extends Component {
    constructor(props) {
        super(props)
        this.NOTIFCATION_TICK_MS = 3000
        this.MS_PER_S = 1000
        this.API = new ReviewMeAPI()
        this.state = {
            issues: [],
            refreshRate: 10,
            checkReviews: false,
            checkSMS: false,
            checkSlack: false,
            checkNotifications: false
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
    handleSlack = (e, checked) => this.setState({ checkSlack: checked })
    handleNotifications = (e, checked) => this.setState({ checkNotifications: checked })
    componentDidMount() {
        console.log('Dashbaord mount')
        let ms = this.state.refreshRate * this.MS_PER_S
        this.tickTimer = setInterval(this.tick, ms)
        this.notificationTickTimer = setInterval(this.notifcationTick, this.NOTIFCATION_TICK_MS)
    }
    componentWillUnmount() {
        console.log('Dashbaord unmount')
        clearInterval(this.tickTimer)
        clearInterval(this.notificationTickTimer)
    }
    render() {
        return (
            <div className="content">
                <Grid fluid>
                    <Row>
                        <Col>
                            <Switch onChange={this.handleReviews} checked={this.state.checkReviews} /> Ask for Reviews
                            <span>, Rate: <Input type="number"
                                placeholder="Rate"
                                style={{ width: '40px' }}
                                value={this.state.refreshRate}
                                onChange={this.handleRefreshRate} />s
                            </span>
                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <Switch onChange={this.handleNotifications} checked={this.state.checkNotifications} /> Check for Unread Notifications
                        </Col>
                    </Row>
                </Grid>
            </div>
        );
    }
}

export default Dashboard;
