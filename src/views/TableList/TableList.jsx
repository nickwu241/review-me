import React, { Component } from 'react';
import { Grid, Row, Col, Table } from 'react-bootstrap';

import Card from '../../components/Card/Card.jsx';

import { LinearProgress } from 'material-ui/Progress'
import ReviewMeAPI from '../../ReviewMeAPI'
import Store from '../../Store'

class TableList extends Component {
    constructor(props) {
        super(props)
        this.API = new ReviewMeAPI()
        this.state = {
            loading: false,
            thArray: ["Repository", "Title", "#", "Status", "Created By", "Created At", "Labels"],
            tdArray: []
        }
    }
    fetch = repos => {
        this.setState({ loading: true })
        this.API.issues(repos, issues => {
            this.setState({
                loading: false,
                tdArray: issues.map(i => [
                    [i.repo_name, i.repo_url],
                    [i.title, i.url],
                    i.number,
                    i.state,
                    i.username,
                    i.created_at,
                    i.labels.map(l => l['name']).join(', ')])
            })
        })
    }
    componentDidMount() {
        if (Store.reposTracking.length > 0) {
            this.fetch(Store.reposTracking)
        }
    }
    render() {
        return (
            <div className="content">
                <Grid fluid>
                    <Row>
                        <Col md={12}>
                            <Card
                                title="Issues"
                                category="All issues in one place"
                                ctTableFullWidth ctTableResponsive
                                content={
                                    (this.state.loading && <LinearProgress color="secondary" />) ||
                                    <Table striped hover>
                                        <thead>
                                            <tr>
                                                {
                                                    this.state.thArray.map((prop, key) => {
                                                        return (
                                                            <th key={key}>{prop}</th>
                                                        );
                                                    })
                                                }
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {
                                                this.state.tdArray.map((prop, key) => {
                                                    return (
                                                        <tr key={key}>{
                                                            prop.map((prop, key) => {
                                                                return (
                                                                    <td key={key}>
                                                                        {(key === 0 || key === 1) && <a href={prop[1]} style={{ color: '#6cc644' }}>{prop[0]}</a>}
                                                                        {(key >= 2) && prop}
                                                                    </td>
                                                                );
                                                            })
                                                        }</tr>
                                                    )
                                                })
                                            }
                                        </tbody>
                                    </Table>
                                }
                            />
                        </Col>
                    </Row>
                </Grid>
            </div>
        );
    }
}

export default TableList;
