# User Manual: Model Operation Guide

## Overview

This manual provides comprehensive instructions for users to effectively operate the application, review entity assessments, and collaborate with the technical team through structured feedback mechanisms.

---

## 1. Initial Authentication

Before accessing the application, users must complete the authentication process:

1. **Azure Login Certification**: All users are required to authenticate using Azure Active Directory credentials
2. **Certificate Requirement**: Access is granted exclusively through valid certificate-based authentication
3. Upon successful authentication, you will be redirected to the main application interface

---

## 2. Session Management

Upon entering the application, users have two primary options:

### Option A: Load Existing Session
- Access previously saved work sessions
- Resume analysis from your last checkpoint
- Review historical assessments and modifications

### Option B: Process New Articles
- Upload one or multiple articles for analysis
- Initiate a new assessment session
- The system will process the submitted content and generate entity evaluations

---

## 3. Interactive Review and Feedback

During an active session, users have full capability to:

- **Review Content**: Examine each feature and its associated data
- **Modify Assessments**: Update entity classifications and descriptions as needed
- **Provide Feedback**: Share observations and corrections with the technical team
- **Collaborate**: Ensure accuracy through iterative refinement of the model's outputs

---

## 4. Activities Table: Crime Entity Flagging

### Overview

The Activities Table serves as the central interface for reviewing entities flagged for criminal activities. This table is dynamically generated based on detected violations.

### Predefined Crime Categories

The Financial Crime Prevention (FCP) team has established a comprehensive list of approximately twelve specific crime categories that the system monitors. These categories represent the full scope of criminal activities the model is designed to detect.

### Dynamic Table Structure

The Activities Table employs an intelligent display mechanism:

- **Conditional Column Display**: Only crime categories with detected violations appear in the table
- **Automatic Filtering**: If no entity has been flagged for a specific crime type, that column is automatically removed from the view
- **Optimized Presentation**: This ensures users focus only on relevant, active violations

### Table Columns

#### 1. Crime Category Columns (Boolean)
- Each displayed column represents a specific crime type
- **Visual Indicators**:
  - ✓ (Checkmark): Entity has committed this crime
  - ✗ (Cross): Entity has not committed this crime
- Only columns with at least one flagged entity are displayed

#### 2. Description Column
- **Entity Information**: Provides detailed context about the flagged entity
- **Reasoning**: Contains the rationale for why the LLM flagged this entity
- **Transparency**: Offers insight into the model's decision-making process

#### 3. Comment Column
- **User Input Field**: Allows users to add contextual notes or observations
- **Collaboration**: Facilitates communication between reviewers
- **Audit Trail**: Documents user assessments and clarifications

### Editing Functionality

Users have comprehensive control over table content through an intuitive editing workflow:

#### Initiating Edit Mode
1. Click the **"Edit"** button to enter modification mode
2. Three additional control buttons will appear:
   - **View Table**: Return to read-only display mode
   - **Save Changes**: Commit all modifications to the system
   - **Reset Table**: Restore the original, system-generated table

#### Available Modifications

While in edit mode, users can:

- **Add Crimes**: Flag an entity for additional crime categories
- **Remove Crimes**: Unflag incorrectly classified entities
- **Modify Descriptions**: Update or clarify entity information and reasoning
- **Add Comments**: Insert observations, questions, or additional context
- **Update Existing Data**: Refine any table content as needed

#### Reset Functionality

The **Reset Table** button provides a safety mechanism:

- Discards all unsaved modifications
- Restores the table to its original, system-generated state
- Allows users to start fresh if needed
- Does not affect previously saved changes

---

## 5. Workflow Summary

1. **Authenticate** using Azure certificate-based login
2. **Choose** between loading an existing session or processing new articles
3. **Review** the Activities Table and entity assessments
4. **Edit** as necessary, making corrections and adding context
5. **Save** your changes or reset to default if needed
6. **Provide feedback** to support continuous model improvement

---

## Support and Assistance

For technical issues, questions about specific flagged entities, or general assistance, please contact the technical team through the application's feedback mechanism.










# User Manual: Graph Visualization and Entity Analysis Features

## Overview

This section describes the advanced visualization and entity analysis capabilities available in the application, including interactive network graphs, relationship mapping, and comprehensive entity summaries.

---

## 6. Feature Graph: Interactive Network Visualization

### Overview

The Feature Graph provides a powerful visual representation of all entities and their interconnections using the Streamlit Link Analysis package. This interactive network diagram enables users to explore complex relationships and identify patterns across flagged entities.

### Graph Components

#### Nodes
Each node in the graph represents a distinct entity and displays:

- **Entity Type Identification**:
  - Natural Person (individual)
  - Company (organization)
- **Flagging Status**: Visual indication of whether the entity has been flagged for criminal activity
- **Interactive Elements**: Clickable nodes that reveal detailed information

#### Edges
Edges (connecting lines) represent relationships between entities:

- **Relationship Type**: The nature of the connection between entities (e.g., ownership, partnership, transaction, affiliation)
- **LLM-Determined**: Relationship classifications are automatically identified and categorized by the language model
- **Visual Clarity**: Lines connect related entities, creating a comprehensive network view

### Interactive Features

#### Navigation and Manipulation

Users can interact with the graph through intuitive controls:

- **Drag and Reposition**: Click and drag any node to rearrange the graph layout
- **Edge Adjustment**: Move edges by repositioning their connected nodes
- **Dynamic Layout**: The graph responds to user manipulation, allowing for customized views
- **Zoom and Pan**: Adjust the view to focus on specific areas of interest

#### Detailed Information Access

- **Click on Node**: Select any node to display comprehensive entity information
- **Contextual Details**: View entity type, flagging status, related crimes, and additional metadata
- **Quick Reference**: Access key information without leaving the graph view

### Use Cases

The Feature Graph is particularly valuable for:

- Identifying networks of related entities
- Discovering indirect connections between flagged individuals and organizations
- Visualizing patterns of criminal activity across multiple entities
- Conducting comprehensive relationship analysis

---

## 7. Relationship Details Table

### Overview

The Relationship Details Table provides a structured, tabular representation of all connections identified in the Feature Graph. This complementary view offers users an alternative method for reviewing and analyzing entity relationships.

### Table Structure

The table displays all entity relationships with the following information:

- **Source Entity**: The originating entity in the relationship
- **Target Entity**: The connected entity in the relationship
- **Relationship Type**: The nature of the connection (as determined by the LLM)
- **Entity Types**: Classification of both entities (natural person or company)
- **Flagging Status**: Indication of whether either entity has been flagged

### Functionality

Users can:

- **Browse All Relationships**: View the complete set of entity connections in a single table
- **Sort and Filter**: Organize relationships by various criteria
- **Cross-Reference**: Compare table data with the visual graph representation
- **Export**: Generate reports based on relationship data

### Benefits

The Relationship Details Table provides:

- **Comprehensive Overview**: See all relationships at a glance
- **Structured Analysis**: Examine connections in a systematic, organized format
- **Documentation**: Create records of entity networks for reporting purposes
- **Accessibility**: Alternative format for users who prefer tabular data

---

## 8. Entity Summaries

### Overview

The Entity Summaries feature provides flexible access to detailed information about individual entities or the entire entity dataset. This feature serves as a comprehensive reference tool for in-depth entity analysis.

### Access Methods

Users can retrieve entity information through multiple pathways:

#### Method A: Dropdown Selection
1. **Dropdown Menu**: Access a list of all entities in the system
2. **Select Entity**: Choose a specific entity from the dropdown
3. **View Summary**: Instantly display comprehensive information about the selected entity

#### Method B: Search Functionality
1. **Search Bar**: Enter the entity name directly
2. **Quick Lookup**: Retrieve entity information by typing (partial or complete names supported)
3. **Instant Results**: View the summary immediately upon selection

#### Method C: View All Entities
1. **"View All Entities" Button**: Click to access the complete dataset
2. **Comprehensive Table**: Display all entities and their descriptions in a single table
3. **Bulk Overview**: Review the entire entity population simultaneously

### Summary Content

Each entity summary includes:

- **Entity Name**: Full identification of the person or organization
- **Entity Type**: Classification as natural person or company
- **Description**: Detailed information about the entity's characteristics and activities
- **Flagging Status**: Whether the entity has been flagged for criminal activity
- **Associated Crimes**: List of specific violations (if applicable)
- **Reasoning**: LLM-generated explanation for any flags
- **Relationship Context**: Overview of connections to other entities

### Table Display (View All Entities)

When viewing all entities in table format, users can:

- **Browse**: Scroll through the complete entity list
- **Sort**: Organize entities by name, type, or flagging status
- **Filter**: Focus on specific subsets (e.g., only flagged entities, only companies)
- **Search**: Use table search functionality to quickly locate specific entries
- **Compare**: Analyze multiple entities side-by-side

### Use Cases

The Entity Summaries feature supports various analytical needs:

- **Individual Investigation**: Deep dive into a specific entity's profile
- **Comparative Analysis**: Review multiple entities to identify patterns
- **Comprehensive Auditing**: Examine the entire entity dataset systematically
- **Quick Reference**: Rapidly access entity information during reviews
- **Documentation**: Generate detailed records for reporting and compliance

---

## 9. Integrated Workflow: Graph, Relationships, and Summaries

These three features work together to provide a complete analytical toolkit:

1. **Visual Exploration**: Use the Feature Graph to identify interesting connections
2. **Detailed Review**: Examine specific relationships in the Relationship Details Table
3. **Deep Analysis**: Access comprehensive entity information through Entity Summaries
4. **Iterative Investigation**: Move fluidly between visualization and detailed data as needed

This integrated approach enables thorough, efficient analysis of complex entity networks and supports informed decision-making in financial crime prevention.

---

## Support and Best Practices

For optimal use of these features:

- Start with the Feature Graph for high-level network understanding
- Use Entity Summaries for focused, detailed investigation
- Reference the Relationship Details Table for structured analysis
- Leverage all three features together for comprehensive reviews

For technical assistance or questions about specific entities or relationships, contact the technical team through the application's feedback mechanism.
