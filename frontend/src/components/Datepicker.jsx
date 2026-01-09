import {Row,Col} from "react-bootstrap";
import Button from "react-bootstrap/Button";
import React, { useState } from 'react';
import { Form } from 'react-bootstrap/Form';

const DatePicker = () => {
    const [date, setDate] = useState('');

    const handleDateChange = (event) => {
        setDate(event.target.value);
    };

    return (
      
        <Form><Row>
             <Col>
            <Form.Group controlId="datePicker">
                <Form.Label>Select a Date</Form.Label>
                <Form.Control
                    type="date"
                    value={date}
                    placeholder="From Date"
                />
            </Form.Group>
            </Col>
             <Col>
            <Form.Group controlId="datePicker">
                <Form.Label>Select a Date</Form.Label>
                <Form.Control type="date" value={date} placeholder="To Date"/>
            </Form.Group>
            </Col>
            </Row>
        </Form> 
    );
};

export default DatePicker;