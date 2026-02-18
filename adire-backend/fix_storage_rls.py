import os
from app import get_db_connection
import psycopg2

def fix_storage_policy():
    print("Connecting to database...")
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database.")
            return

        cur = conn.cursor()
        
        # SQL to enable RLS (it's enabled by default on storage.objects) 
        # and add policies for public access to 'product-image' bucket.
        
        # We use a DO block to safely check and create policies
        sql = """
        DO $$
        BEGIN
            -- 1. Allow Public INSERT (Uploads)
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND schemaname = 'storage' AND policyname = 'Public Access Insert'
            ) THEN
                CREATE POLICY "Public Access Insert" ON storage.objects
                FOR INSERT TO public
                WITH CHECK (bucket_id = 'product-image');
            END IF;

            -- 2. Allow Public SELECT (Downloads - usually redundant if bucket is public, but good for safety)
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND schemaname = 'storage' AND policyname = 'Public Access Select'
            ) THEN
                CREATE POLICY "Public Access Select" ON storage.objects
                FOR SELECT TO public
                USING (bucket_id = 'product-image');
            END IF;

            -- 3. Allow Public UPDATE (In case of overwrites)
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND schemaname = 'storage' AND policyname = 'Public Access Update'
            ) THEN
                CREATE POLICY "Public Access Update" ON storage.objects
                FOR UPDATE TO public
                USING (bucket_id = 'product-image');
            END IF;
            
             -- 4. Allow Public DELETE (For replacing/deleting images)
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'objects' AND schemaname = 'storage' AND policyname = 'Public Access Delete'
            ) THEN
                CREATE POLICY "Public Access Delete" ON storage.objects
                FOR DELETE TO public
                USING (bucket_id = 'product-image');
            END IF;
        END
        $$;
        """
        
        print("Executing SQL to fix storage policies...")
        cur.execute(sql)
        conn.commit()
        print("Policies applied successfully!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_storage_policy()
