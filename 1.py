from flask import Flask
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
import numpy as np
from flaskext.mysql import MySQL
app= Flask(__name__)
def getConnect(server, port, database, username, password):
    try:
        mysql = MySQL()
        app.config['MYSQL_DATABASE_HOST'] = server
        app.config['MYSQL_DATABASE_PORT'] = port
        app.config['MYSQL_DATABASE_USER'] = username
        app.config['MYSQL_DATABASE_PASSWORD'] = password
        app.config['MYSQL_DATABASE_DB'] = database
        mysql.init_app(app)
        return mysql.connect()
    except Exception as e:
        print("Loi ket noi den MySQL:", e)
        return None
def closeConnection(conn):
    if conn!=None:
        conn.close()

def queryDataset(conn,sql):
    cursor=conn.cursor()
    
    cursor.execute(sql)
    df=pd.DataFrame(cursor.fetchall())
    return df

conn=getConnect('localhost',3306,'salesdatabase','root','PkHbr@2f3oOtRH9O4!Cu')

sql1="select * from customer"
df1=queryDataset(conn,sql1)
print(df1)

sql2="select distinct customer.CustomerId, Age, Annual_Income, Spending_Score "\
    "from customer, customer_spend_score "\
    "where customer.CustomerId=customer_spend_score.CustomerID"
    
df2=queryDataset(conn,sql2)
df2.columns=['CustomerId','Age','Annual Income','Spending Score']
print(df2)
print(df2.head())
print(df2.describe())

def showHistogram (df, columns):
    plt.figure(1, figsize=(7,8))
    n=0
    for column in columns:
        n+=1
        plt.subplot(3,1,n)
        plt.subplots_adjust(hspace=0.5)
        sns.histplot(data=df, x=column, kde=True)
        plt.title(f'Histogram of {column}')
    plt.show()
showHistogram(df2,df2.columns[1:])

def elbowMenthod(df, columnsForElbow):
    x=df.loc[:, columnsForElbow].values
    inertia=[]
    for n in range (1,11):
        model = KMeans (n_clusters=n,
                        init = 'k-means++',
                        max_iter=500,
                        random_state=42)
        model.fit(x)
        inertia.append(model.inertia_)
    plt.figure(1, figsize=(15,6))
    plt.plot(np.arange(1,11), inertia, 'o-')
    plt.plot(np.arange(1,11), inertia, '-', alpha=0.5)
    plt.xlabel('Number of Cluster'), plt.ylabel('Cluster sum of sq distances')
    plt.show()
    
    columns = ['Age', 'Spending Score']
    elbowMenthod(df2,columns)
    
    def runKMeans(X, cluster):
        model = KMeans (n_clusters=n,
                        init = 'k-means++',
                        max_iter=500,
                        random_state=42)
        model.fit(X)
        labels=model.labels_
        centroids = model.cluster_centers_
        y_means = model.fit_predict(X)
        return y_means, centroids, labels
X=df2.loc[:,columns].values
cluster = 4
colors = ["red", "green", "blue","purple","black", "pink","orange"]

y_kmeans, centroids, labels=runKMeans(X, cluster)
print(y_kmeans)
print(centroids)
print(labels)
df2["cluster"]=labels 
import matplotlib.pyplot as plt

def visualizeKMeans(X, y_kmeans, cluster, title, xlabel, ylabel, colors):
    plt.figure(figsize=(10, 10))
    for i in range(cluster):
        plt.scatter(X[y_kmeans == i, 0],
                    X[y_kmeans == i, 1],
                    s=100,
                    c=colors[i],
                    label='Cluster %i' % (i+1))

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()
visualizeKMeans(X,
                y_kmeans,
                cluster,
                "Cluster of cus - Age x spending",
                "Age",
                "Spending Score",
                colors)