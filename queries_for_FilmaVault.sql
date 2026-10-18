-- Q1 Answers: What is showing, where, and when (all screenings) --
Select f.film_name, c.city, s.session_time From Screening s 
Join Film f On s.film_id = f.film_id
Join Cinema c On s.cinema_id = c.cinema_id
Order by f.film_name;
--Q2 Answers: What a specific viewer has booked (Viewer's booking details) --
Select v.first_name, v.last_name, f.film_name, c.city, s.session_time, t.seat_no From Ticket t
Join Viewer v On t.viewer_id = v.viewer_id
Join Screening s On t.screening_id = s.screening_id
Join Film f On s.film_id = f.film_id
Join Cinema c On s.cinema_id = c.cinema_id
Where v.viewer_id = 'V006';
-- Q3 Answers: What the most popular film by ticket sold --
Select f.film_name, COUNT(t.ticket_no) As tickets_sold From Ticket t
Join Screening s On t.screening_id = s.screening_id
Join Film f On s.film_id = f.film_id
Group By f.film_name Order By tickets_sold DESC;
-- Q4 Answers: How many tickets have been sold per city (busiest cinema) --
Select c.city, COUNT(t.ticket_no) As tickets_sold From Ticket t
Join Screening s On t.screening_id = s.screening_id
Join Cinema c On s.cinema_id = c.cinema_id
Group By c.city Order By tickets_sold DESC;
--Q5 Answers: Who the most engaged viewers are by number of different films they've seen --
Select v.first_name, v.last_name, Count(Distinct f.film_id) As different_films From Ticket t
Join Viewer v On t.viewer_id = v.viewer_id
Join Screening s On t.screening_id = s.screening_id
Join Film f On s.film_id = f.film_id
Group By v.viewer_id Order By different_films DESC
Limit 10;
-- Q6 Answers: Films grouped by director --
Select d.director_name, f.film_name, f.genre From Film f
Join Director d On f.director_id = d.director_id
Order By d.director_name;