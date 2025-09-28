# **Database Schema: Klimaneustart Civic Dialogue App**

## 1. Overview

This document outlines the database schema for the Klimaneustart application. The design is normalized to ensure data integrity, scalability for future analytics, and strict compliance with GDPR by isolating Personally Identifiable Information (PII).

---

## 2. Schema Tables

### `users`

**Purpose:** Note-maker information. Essential for future multi-user support.

| Column Name | Data Type | Constraints/Notes                     |
| ----------- | --------- | ------------------------------------- |
| id          | INTEGER   | PRIMARY KEY, Auto-incrementing        |
| username    | TEXT      | NOT NULL, UNIQUE                      |
| created_at  | TIMESTAMP | NOT NULL, Default `CURRENT_TIMESTAMP` |

---

### `themes`

**Purpose:** A lookup table for all possible interest areas (e.g., Urban Garden).

| Column Name | Data Type | Constraints/Notes |
| ----------- | --------- | ----------------- |
| id          | TEXT      | PRIMARY KEY       |
| name        | TEXT      | NOT NULL          |
| description | TEXT      |                   |

---

### `initiatives`

**Purpose:** A lookup table for all partner initiatives.

| Column Name | Data Type | Constraints/Notes |
| ----------- | --------- | ----------------- |
| id          | TEXT      | PRIMARY KEY       |
| name        | TEXT      | NOT NULL          |
| description | TEXT      | NOT NULL          |
| link        | TEXT      | NOT NULL          |

---

### `dialogues`

**Purpose:** The central table for each conversation session. Contains all non-PII data.

| Column Name           | Data Type | Constraints/Notes                        |
| --------------------- | --------- | ---------------------------------------- |
| id                    | INTEGER   | PRIMARY KEY, Auto-incrementing           |
| user_id               | INTEGER   | NOT NULL, Foreign Key to `users.id`      |
| notes                 | TEXT      | General notes from the dialogue          |
| audio_note_url        | TEXT      | Link to a cloud-stored audio file        |
| observer_reflection   | TEXT      | The facilitator's reflection             |
| surprise              | TEXT      | What surprised the facilitator           |
| num_people            | INTEGER   | NOT NULL                                 |
| duration              | INTEGER   | NOT NULL, Duration in minutes            |
| location              | TEXT      | Optional text location (e.g., park name) |
| is_anonymous          | BOOLEAN   | NOT NULL, Master GDPR flag               |
| consent_share_contact | BOOLEAN   | NOT NULL, Specific consent to store PII  |
| created_at            | TIMESTAMP | NOT NULL, Default `CURRENT_TIMESTAMP`    |

---

### `participant_contact`

**Purpose:** The PII Vault. This table is strictly isolated and should only be accessed under specific conditions. Only write to this table if `dialogues.is_anonymous` is FALSE **AND** `dialogues.consent_share_contact` is TRUE.

| Column Name  | Data Type | Constraints/Notes                          |
| ------------ | --------- | ------------------------------------------ |
| dialogue_id  | INTEGER   | PRIMARY KEY, Foreign Key to `dialogues.id` |
| contact_info | TEXT      | NOT NULL                                   |

---

## 3. Linking Tables (Many-to-Many Relationships)

### `initiative_districts`

**Purpose:** Links initiatives to the districts they operate in.

| Column Name   | Data Type | Constraints/Notes                                 |
| ------------- | --------- | ------------------------------------------------- |
| initiative_id | TEXT      | PRIMARY KEY part, Foreign Key to `initiatives.id` |
| district_name | TEXT      | PRIMARY KEY part                                  |

---

### `initiative_themes`

**Purpose:** Links initiatives to the themes (interest areas) they cover.

| Column Name   | Data Type | Constraints/Notes                                 |
| ------------- | --------- | ------------------------------------------------- |
| initiative_id | TEXT      | PRIMARY KEY part, Foreign Key to `initiatives.id` |
| theme_id      | TEXT      | PRIMARY KEY part, Foreign Key to `themes.id`      |

---

### `dialogue_districts`

**Purpose:** Links a dialogue to all districts mentioned.

| Column Name   | Data Type | Constraints/Notes                               |
| ------------- | --------- | ----------------------------------------------- |
| dialogue_id   | INTEGER   | PRIMARY KEY part, Foreign Key to `dialogues.id` |
| district_name | TEXT      | PRIMARY KEY part                                |

---

### `dialogue_interest_areas`

**Purpose:** Links a dialogue to all participant interest areas.

| Column Name      | Data Type | Constraints/Notes                               |
| ---------------- | --------- | ----------------------------------------------- |
| dialogue_id      | INTEGER   | PRIMARY KEY part, Foreign Key to `dialogues.id` |
| interest_area_id | TEXT      | PRIMARY KEY part, Foreign Key to `themes.id`    |

---

### `dialogue_topic_selections`

**Purpose:** Links a dialogue to all specific sub-topics discussed. This is the most granular data.

| Column Name        | Data Type | Constraints/Notes                       |
| ------------------ | --------- | --------------------------------------- |
| id                 | INTEGER   | PRIMARY KEY, Auto-incrementing          |
| dialogue_id        | INTEGER   | NOT NULL, Foreign Key to `dialogues.id` |
| main_topic_id      | TEXT      | NOT NULL (e.g., `'wohnen_bauwende'`)    |
| sub_group_id       | TEXT      | NOT NULL (e.g., `'transport'`)          |
| selected_option_id | TEXT      | NOT NULL (e.g., `'bicycle'`)            |
| custom_note        | TEXT      | Optional note for this sub-group        |

---
