--
-- PostgreSQL database dump
--

\restrict JJcnNQg4Gqk034RgRS72jdWTSYT8exuadY4VehBPVK0aSEzlYu0qKwvehKBLqEf

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_execution_traces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_execution_traces (
    id uuid NOT NULL,
    planning_session_id uuid NOT NULL,
    tool_name character varying(100) NOT NULL,
    tool_input jsonb,
    tool_output jsonb,
    success boolean NOT NULL,
    iteration_number integer NOT NULL
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: attractions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attractions (
    id uuid NOT NULL,
    destination_id uuid NOT NULL,
    category character varying(100) NOT NULL,
    opening_hours jsonb,
    entry_fee numeric(10,2) NOT NULL,
    duration_hours numeric(4,2)
);


--
-- Name: conversation_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_history (
    id uuid NOT NULL,
    planning_session_id uuid,
    role character varying(20) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: destinations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.destinations (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    country character varying(100) NOT NULL,
    region character varying(100),
    coordinates json,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feedback (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    rating integer NOT NULL,
    comment text,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: hotels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hotels (
    id uuid NOT NULL,
    destination_id uuid NOT NULL,
    price_per_night numeric(10,2) NOT NULL,
    facilities text[],
    rating numeric(2,1),
    photo_urls text[],
    is_active boolean NOT NULL
);


--
-- Name: itineraries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.itineraries (
    id uuid NOT NULL,
    trip_id uuid NOT NULL,
    total_estimated_cost numeric(10,2) NOT NULL,
    route_info jsonb,
    weather_info jsonb,
    share_token character varying(255)
);


--
-- Name: itinerary_day_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.itinerary_day_items (
    id uuid NOT NULL,
    itinerary_day_id uuid NOT NULL,
    item_type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    start_time time without time zone,
    end_time time without time zone,
    location character varying(255),
    estimated_cost numeric(10,2),
    sort_order integer NOT NULL
);


--
-- Name: itinerary_days; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.itinerary_days (
    id uuid NOT NULL,
    itinerary_id uuid NOT NULL,
    day_number integer NOT NULL,
    date date NOT NULL,
    title character varying(255) NOT NULL,
    summary text
);


--
-- Name: local_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.local_events (
    id uuid NOT NULL,
    destination_id uuid NOT NULL,
    event_schedule jsonb NOT NULL
);


--
-- Name: planning_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.planning_sessions (
    id uuid NOT NULL,
    trip_id uuid NOT NULL,
    working_memory jsonb,
    status character varying(50) NOT NULL,
    iteration_count integer NOT NULL,
    progress_message text,
    progress_percentage integer NOT NULL
);


--
-- Name: restaurants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.restaurants (
    id uuid NOT NULL,
    destination_id uuid NOT NULL,
    cuisine_type character varying(100) NOT NULL,
    avg_meal_cost numeric(10,2) NOT NULL
);


--
-- Name: transport_rates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transport_rates (
    id uuid NOT NULL,
    transport_type character varying(50) NOT NULL,
    cost_per_km numeric(10,2) NOT NULL,
    base_fare numeric(10,2) NOT NULL
);


--
-- Name: trips; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trips (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    status character varying(20) NOT NULL,
    travel_start_date date NOT NULL,
    travel_end_date date NOT NULL,
    duration integer NOT NULL,
    budget numeric(10,2) NOT NULL,
    travel_style character varying(100) NOT NULL,
    accommodation_preference character varying(100) NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    full_name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(30) NOT NULL,
    is_active boolean NOT NULL,
    is_email_verified boolean NOT NULL,
    email_verification_token character varying(255),
    email_verification_expiry timestamp with time zone,
    password_reset_token character varying(255),
    reset_token_expiry timestamp with time zone,
    refresh_token character varying(500),
    refresh_token_expiry timestamp with time zone,
    preferred_travel_style character varying(100),
    preferred_accommodation character varying(100),
    typical_budget_range character varying(100),
    interests text[],
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: agent_execution_traces agent_execution_traces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_execution_traces
    ADD CONSTRAINT agent_execution_traces_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attractions attractions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attractions
    ADD CONSTRAINT attractions_pkey PRIMARY KEY (id);


--
-- Name: conversation_history conversation_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_history
    ADD CONSTRAINT conversation_history_pkey PRIMARY KEY (id);


--
-- Name: destinations destinations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.destinations
    ADD CONSTRAINT destinations_pkey PRIMARY KEY (id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: hotels hotels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_pkey PRIMARY KEY (id);


--
-- Name: itineraries itineraries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itineraries
    ADD CONSTRAINT itineraries_pkey PRIMARY KEY (id);


--
-- Name: itineraries itineraries_share_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itineraries
    ADD CONSTRAINT itineraries_share_token_key UNIQUE (share_token);


--
-- Name: itinerary_day_items itinerary_day_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itinerary_day_items
    ADD CONSTRAINT itinerary_day_items_pkey PRIMARY KEY (id);


--
-- Name: itinerary_days itinerary_days_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itinerary_days
    ADD CONSTRAINT itinerary_days_pkey PRIMARY KEY (id);


--
-- Name: local_events local_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_events
    ADD CONSTRAINT local_events_pkey PRIMARY KEY (id);


--
-- Name: planning_sessions planning_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planning_sessions
    ADD CONSTRAINT planning_sessions_pkey PRIMARY KEY (id);


--
-- Name: restaurants restaurants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_pkey PRIMARY KEY (id);


--
-- Name: transport_rates transport_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transport_rates
    ADD CONSTRAINT transport_rates_pkey PRIMARY KEY (id);


--
-- Name: trips trips_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: agent_execution_traces agent_execution_traces_planning_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_execution_traces
    ADD CONSTRAINT agent_execution_traces_planning_session_id_fkey FOREIGN KEY (planning_session_id) REFERENCES public.planning_sessions(id);


--
-- Name: attractions attractions_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attractions
    ADD CONSTRAINT attractions_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.destinations(id);


--
-- Name: conversation_history conversation_history_planning_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_history
    ADD CONSTRAINT conversation_history_planning_session_id_fkey FOREIGN KEY (planning_session_id) REFERENCES public.planning_sessions(id);


--
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: hotels hotels_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.destinations(id);


--
-- Name: itineraries itineraries_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itineraries
    ADD CONSTRAINT itineraries_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trips(id);


--
-- Name: itinerary_day_items itinerary_day_items_itinerary_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itinerary_day_items
    ADD CONSTRAINT itinerary_day_items_itinerary_day_id_fkey FOREIGN KEY (itinerary_day_id) REFERENCES public.itinerary_days(id);


--
-- Name: itinerary_days itinerary_days_itinerary_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.itinerary_days
    ADD CONSTRAINT itinerary_days_itinerary_id_fkey FOREIGN KEY (itinerary_id) REFERENCES public.itineraries(id);


--
-- Name: local_events local_events_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.local_events
    ADD CONSTRAINT local_events_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.destinations(id);


--
-- Name: planning_sessions planning_sessions_trip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.planning_sessions
    ADD CONSTRAINT planning_sessions_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trips(id);


--
-- Name: restaurants restaurants_destination_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.restaurants
    ADD CONSTRAINT restaurants_destination_id_fkey FOREIGN KEY (destination_id) REFERENCES public.destinations(id);


--
-- Name: trips trips_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trips
    ADD CONSTRAINT trips_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict JJcnNQg4Gqk034RgRS72jdWTSYT8exuadY4VehBPVK0aSEzlYu0qKwvehKBLqEf

