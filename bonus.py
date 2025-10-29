from flask import Flask, request, render_template_string
import pandas as pd
import numpy as np
import plotly.express as px
import plotly
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from flaskext.mysql import MySQL
from decimal import Decimal


app = Flask(__name__)

# ================== KẾT NỐI MySQL (Sakila) ==================
def getConnect(host, port, db, user, pwd):
    mysql = MySQL()
    app.config['MYSQL_DATABASE_HOST'] = host
    app.config['MYSQL_DATABASE_PORT'] = port
    app.config['MYSQL_DATABASE_USER'] = user
    app.config['MYSQL_DATABASE_PASSWORD'] = pwd
    app.config['MYSQL_DATABASE_DB'] = db
    mysql.init_app(app)
    return mysql.connect()

conn = getConnect('localhost', 3306, 'sakila', 'root', 'PkHbr@2f3oOtRH9O4!Cu')

def qdf(sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    cols = [c[0] for c in cur.description]
    return pd.DataFrame(cur.fetchall(), columns=cols)

# ================== (1) KHÁCH HÀNG THEO PHIM ==================
def customers_by_film_all():
    # mỗi phim → danh sách KH đã thuê + số lần thuê (để sắp xếp); không lọc -> dùng ở trang tổng hợp
    sql = """
    SELECT f.film_id, f.title,
           c.customer_id,
           CONCAT(c.first_name,' ',c.last_name) AS customer_name,
           COUNT(r.rental_id) AS rental_count
    FROM rental r
    JOIN inventory i  USING (inventory_id)
    JOIN film f       USING (film_id)
    JOIN customer c   USING (customer_id)
    GROUP BY f.film_id, c.customer_id
    ORDER BY f.title, rental_count DESC, customer_name;
    """
    return qdf(sql)

def customers_by_film(film_id:int):
    # chi tiết cho 1 phim, đã loại trùng KH
    sql = """
    SELECT DISTINCT
           f.film_id, f.title,
           c.customer_id, CONCAT(c.first_name,' ',c.last_name) AS customer_name
    FROM rental r
    JOIN inventory i  USING (inventory_id)
    JOIN film f       USING (film_id)
    JOIN customer c   USING (customer_id)
    WHERE f.film_id = %s
    ORDER BY customer_name;
    """
    return qdf(sql, (film_id,))

# ================== (2) KHÁCH HÀNG THEO CATEGORY ==================
def customers_by_category_all():
    # tổng hợp: mỗi category → list KH (đã loại trùng), kèm rental_count để sắp
    sql = """
    SELECT cat.category_id, cat.name AS category,
           c.customer_id,
           CONCAT(c.first_name,' ',c.last_name) AS customer_name,
           COUNT(DISTINCT r.rental_id) AS rental_count
    FROM rental r
    JOIN inventory i      USING (inventory_id)
    JOIN film f           USING (film_id)
    JOIN film_category fc USING (film_id)
    JOIN category cat     USING (category_id)
    JOIN customer c       USING (customer_id)
    GROUP BY cat.category_id, c.customer_id
    ORDER BY category, rental_count DESC, customer_name;
    """
    return qdf(sql)

def customers_by_category(cat_id:int):
    # chi tiết 1 category: KH unique
    sql = """
    SELECT DISTINCT
           cat.category_id, cat.name AS category,
           c.customer_id,
           CONCAT(c.first_name,' ',c.last_name) AS customer_name
    FROM rental r
    JOIN inventory i      USING (inventory_id)
    JOIN film f           USING (film_id)
    JOIN film_category fc USING (film_id)
    JOIN category cat     USING (category_id)
    JOIN customer c       USING (customer_id)
    WHERE cat.category_id = %s
    ORDER BY customer_name;
    """
    return qdf(sql, (cat_id,))

# ================== (3) FEATURES & KMEANS CLUSTERING ==================
def build_customer_features():
    """
    Đề xuất đặc trưng (mức độ quan tâm Film/Inventory):
      - total_rentals: tổng số lần thuê
      - distinct_films: số phim khác nhau đã thuê
      - distinct_categories: số thể loại khác nhau
      - distinct_inventory_items: số inventory_id khác nhau (bám inventory)
      - distinct_stores: số store đã thuê
      - avg_rental_hours: TB thời lượng thuê (giờ)
      - recency_days: số ngày từ lần thuê gần nhất đến hôm nay
    """
    # tổng số lần thuê + gần nhất
    rentals = qdf("""
      SELECT c.customer_id,
             COUNT(*) AS total_rentals,
             MAX(r.rental_date) AS last_rental
      FROM rental r
      JOIN customer c USING (customer_id)
      GROUP BY c.customer_id
    """)

    films = qdf("""
      SELECT c.customer_id,
             COUNT(DISTINCT f.film_id) AS distinct_films
      FROM rental r
      JOIN inventory i  USING (inventory_id)
      JOIN film f       USING (film_id)
      JOIN customer c   USING (customer_id)
      GROUP BY c.customer_id
    """)

    cats = qdf("""
      SELECT c.customer_id,
             COUNT(DISTINCT fc.category_id) AS distinct_categories
      FROM rental r
      JOIN inventory i      USING (inventory_id)
      JOIN film f           USING (film_id)
      JOIN film_category fc USING (film_id)
      JOIN customer c       USING (customer_id)
      GROUP BY c.customer_id
    """)

    invs = qdf("""
      SELECT c.customer_id,
             COUNT(DISTINCT r.inventory_id) AS distinct_inventory_items,
             COUNT(DISTINCT i.store_id)     AS distinct_stores
      FROM rental r
      JOIN inventory i USING (inventory_id)
      JOIN customer c  USING (customer_id)
      GROUP BY c.customer_id
    """)

    dur = qdf("""
      SELECT c.customer_id,
             AVG(TIMESTAMPDIFF(HOUR, r.rental_date, r.return_date)) AS avg_rental_hours
      FROM rental r
      JOIN customer c USING (customer_id)
      WHERE r.return_date IS NOT NULL
      GROUP BY c.customer_id
    """)

    base = qdf("""
      SELECT customer_id, CONCAT(first_name,' ',last_name) AS customer_name
      FROM customer
    """)

    # merge
    df = base.merge(rentals, on='customer_id', how='left') \
             .merge(films,   on='customer_id', how='left') \
             .merge(cats,    on='customer_id', how='left') \
             .merge(invs,    on='customer_id', how='left') \
             .merge(dur,     on='customer_id', how='left')

    # recency_days
    today = qdf("SELECT CURRENT_DATE AS d").iloc[0,0]
    df['recency_days'] = (pd.to_datetime(str(today)) - pd.to_datetime(df['last_rental'])).dt.days.astype(float)
    for c in ['total_rentals','distinct_films','distinct_categories','distinct_inventory_items',
          'distinct_stores','avg_rental_hours']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # fillna
    num_cols = ['total_rentals','distinct_films','distinct_categories',
                'distinct_inventory_items','distinct_stores','avg_rental_hours','recency_days']
    df[num_cols] = df[num_cols].fillna(0)

    return df

def run_kmeans(df_feat: pd.DataFrame, k: int):
    feats = ['total_rentals','distinct_films','distinct_categories',
             'distinct_inventory_items','distinct_stores','avg_rental_hours','recency_days']
    X = df_feat[feats].to_numpy()
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=500, random_state=42)
    labels = km.fit_predict(Xs)
    df_out = df_feat.copy()
    df_out['cluster'] = labels
    return df_out, feats

def cluster_chart_html(df_clustered, feats, k):
    # chọn 3 features có variance cao nhất để vẽ 3D (hoặc fallback 2D)
    variances = df_clustered[feats].var().sort_values(ascending=False).index.tolist()
    cols3 = variances[:3]
    if len(cols3) >= 3:
        fig = px.scatter_3d(df_clustered,
                            x=cols3[0], y=cols3[1], z=cols3[2],
                            color='cluster',
                            hover_data=['customer_id','customer_name']+feats,
                            title=f"KMeans Clustering k={k} (3D): {cols3[0]} / {cols3[1]} / {cols3[2]}")
    else:
        cols2 = variances[:2]
        fig = px.scatter(df_clustered,
                         x=cols2[0], y=cols2[1],
                         color='cluster',
                         hover_data=['customer_id','customer_name']+feats,
                         title=f"KMeans Clustering k={k} (2D): {cols2[0]} vs {cols2[1]}")
    fig.update_layout(margin=dict(l=0,r=0,t=40,b=0))
    return plotly.io.to_html(fig, full_html=False)

def customers_in_cluster(df_clustered, cluster_id:int):
    cols_show = ['customer_id','customer_name','total_rentals','distinct_films',
                 'distinct_categories','distinct_inventory_items','distinct_stores',
                 'avg_rental_hours','recency_days']
    return df_clustered.loc[df_clustered['cluster']==cluster_id, cols_show] \
                       .sort_values(['total_rentals','distinct_films'], ascending=False)

@app.route('/')
def index():
    return """
    <h2 style="text-align:center">Sakila – Customer Exploration</h2>
    <ul>
      <li><a href="/by-film">Khách hàng theo Tên phim</a></li>
      <li><a href="/by-category">Khách hàng theo Category</a></li>
      <li><a href="/cluster?k=5">Gom cụm K-Means (mặc định k=5)</a></li>
    </ul>
    <p>Tip: /by-film?film_id=1, /by-category?category_id=2, /cluster?k=4</p>
    """

# ---- (1) By Film ----
@app.route('/by-film')
def by_film():
    film_id = request.args.get('film_id', type=int)

    if film_id:
        df = customers_by_film(film_id)
        if df.empty:
            body = f"<p>Không tìm thấy khách hàng cho film_id={film_id}</p>"
        else:
            title = df[['film_id','title']].drop_duplicates().iloc[0]
            title_text = f"[{title.film_id}] {title.title}"

            # Biểu đồ: số lượng thuê theo khách hàng
            fig = px.bar(df.groupby('customer_name')['rental_id'].count().reset_index(),
                         x='customer_name', y='rental_id',
                         title=f"Số lần thuê phim '{title_text}' theo khách hàng",
                         labels={'rental_id':'Số lần thuê', 'customer_name':'Khách hàng'})
            fig.update_layout(xaxis_tickangle=-45)
            chart_html = plotly.io.to_html(fig, full_html=False)

            body = f"""
            <h3>Danh sách khách hàng đã thuê phim: {title_text}</h3>
            {chart_html}
            <h4>Chi tiết</h4>
            {df[['customer_id','customer_name','rental_date']].drop_duplicates()
               .sort_values('customer_name')
               .to_html(classes='table table-striped table-bordered', index=False)}
            """
    else:
        df = customers_by_film_all()
        summary = df.groupby(['film_id','title'])['customer_id'].nunique().reset_index(name='unique_customers') \
                    .sort_values('unique_customers', ascending=False)
        fig = px.bar(summary.head(20),
                     x='title', y='unique_customers',
                     title='Top 20 phim có nhiều khách hàng unique nhất',
                     labels={'unique_customers':'Số KH unique', 'title':'Tên phim'})
        fig.update_layout(xaxis_tickangle=-45)
        chart_html = plotly.io.to_html(fig, full_html=False)

        body = f"""
        <h3>Tổng hợp – Số khách hàng unique theo phim</h3>
        {chart_html}
        {summary.to_html(classes='table table-bordered', index=False)}
        <p>Dùng /by-film?film_id=... để xem danh sách khách hàng của 1 phim.</p>
        """

    html = f"""
    <html><head>
      <meta charset="utf-8">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
      <style>body {{ padding: 20px }}</style>
    </head><body>
      <a href="/">⬅ Trang chủ</a>
      {body}
    </body></html>
    """
    return html


# ---- (2) By Category ----
@app.route('/by-category')
def by_category():
    cat_id = request.args.get('category_id', type=int)
    if cat_id:
        df = customers_by_category(cat_id)
        if df.empty:
            body = f"<p>Không tìm thấy khách hàng cho category_id={cat_id}</p>"
        else:
            title = df[['category_id','category']].drop_duplicates().iloc[0]
            title_text = f"[{title.category_id}] {title.category}"

            fig = px.bar(df.groupby('customer_name')['rental_id'].count().reset_index(),
                         x='customer_name', y='rental_id',
                         title=f"Số lần thuê theo khách hàng trong Category '{title_text}'",
                         labels={'rental_id':'Số lần thuê', 'customer_name':'Khách hàng'})
            fig.update_layout(xaxis_tickangle=-45)
            chart_html = plotly.io.to_html(fig, full_html=False)

            body = f"""
            <h3>Khách hàng đã thuê trong Category: {title_text}</h3>
            {chart_html}
            <h4>Chi tiết</h4>
            {df[['customer_id','customer_name','title','rental_date']]
                .drop_duplicates()
                .sort_values('customer_name')
                .to_html(classes='table table-striped table-bordered', index=False)}
            """
    else:
        df = customers_by_category_all()
        summary = df.groupby(['category_id','category'])['customer_id'].nunique().reset_index(name='unique_customers') \
                    .sort_values('unique_customers', ascending=False)
        fig = px.bar(summary.head(15),
                     x='category', y='unique_customers',
                     title='Top Category có nhiều khách hàng nhất',
                     labels={'unique_customers':'Số KH unique','category':'Category'})
        chart_html = plotly.io.to_html(fig, full_html=False)

        body = f"""
        <h3>Tổng hợp – Số khách hàng unique theo Category</h3>
        {chart_html}
        {summary.to_html(classes='table table-bordered', index=False)}
        <p>Dùng /by-category?category_id=... để xem danh sách khách hàng của 1 Category.</p>
        """

    html = f"""
    <html><head>
      <meta charset="utf-8">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
      <style>body {{ padding: 20px }}</style>
    </head><body>
      <a href="/">⬅ Trang chủ</a>
      {body}
    </body></html>
    """
    return html


# ---- (3) Clustering ----
@app.route('/cluster')
def cluster():
    k = request.args.get('k', default=5, type=int)
    feats_df = build_customer_features()

    # convert all numeric columns to float to avoid Decimal issue
    feats_df = feats_df.applymap(lambda x: float(x) if isinstance(x, Decimal) else x)

    # chuẩn hóa
    feats = ['total_rentals','distinct_films','distinct_categories','distinct_inventory_items','avg_rental_hours']
    X = feats_df[feats].fillna(0).astype(float)
    X_scaled = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=k, random_state=42)
    feats_df['cluster'] = km.fit_predict(X_scaled)

    # biểu đồ 3D
    fig = px.scatter_3d(
        feats_df,
        x='total_rentals', y='distinct_films', z='distinct_categories',
        color='cluster',
        hover_data=['customer_id','customer_name'],
        title=f'K-Means Clustering (k={k}) - Sakila Customers'
    )
    chart_html = plotly.io.to_html(fig, full_html=False)

    # bảng theo từng cụm
    tables = []
    for cid in sorted(feats_df['cluster'].unique()):
        sub = customers_in_cluster(feats_df, cid)
        tables.append(f"<h5 style='color:#4b6cb7'>Cụm {cid}</h5>" +
                      sub.to_html(classes='table table-striped table-bordered', index=False))

    page = f"""
    <!doctype html><html lang="vi"><head>
      <meta charset="utf-8">
      <title>Clustering k={k}</title>
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
      <style>body {{ padding: 20px }}</style>
    </head><body>
      <a href="/">⬅ Trang chủ</a>
      <h3>Gom cụm khách hàng (k = {k})</h3>
      <div class="mb-3">
        <form method="get" action="/cluster" class="row g-2">
          <div class="col-auto">
            <input class="form-control" name="k" type="number" min="2" max="12" value="{k}">
          </div>
          <div class="col-auto">
            <button class="btn btn-primary" type="submit">Chạy lại K-Means</button>
          </div>
        </form>
      </div>
      <div class="card mb-4"><div class="card-body">
        {chart_html}
      </div></div>
      <h4>Danh sách khách hàng theo từng cụm</h4>
      {''.join(tables)}
    </body></html>
    """
    return page


# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=True)