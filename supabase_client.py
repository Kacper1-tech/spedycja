from supabase import create_client, Client

# Wstaw tutaj swoje dane z Supabase
SUPABASE_URL = "https://rsmzpmqwolkfhiowwlva.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzbXpwbXF3b2xrZmhpb3d3bHZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwNzMyMDgsImV4cCI6MjA2NTY0OTIwOH0.kl1YLa2WGF88ZKOyEH_ugJlzj9wzcCOl3Xc_8eCQNtg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
