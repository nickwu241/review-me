import React, {Component} from 'react';
import { NavItem, Nav, NavDropdown, MenuItem } from 'react-bootstrap';


class HeaderLinks extends Component{
    render(){
        return (
            <div>
                <Nav pullRight>
                    <NavItem eventKey={1} href="#">Account</NavItem>
                    <NavDropdown eventKey={2} title="Settings" id="basic-nav-dropdown-right">
                        <MenuItem eventKey={2.1}>Secret setting</MenuItem>
                        <MenuItem eventKey={2.2}>Even more secret setting</MenuItem>
                        <MenuItem divider />
                        <MenuItem eventKey={2.5}>No secrets here</MenuItem>
                    </NavDropdown>
                    <NavItem eventKey={3} href="#">Log out</NavItem>
                </Nav>
            </div>
        );
    }
}

export default HeaderLinks;
