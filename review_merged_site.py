from newsletter_tools.my_functions import *

# Params
repo_owner = 'InseeFrLab'
repo_name='ssphub'
subfolder_path='project'
branch='review_project'

# Fetch all folder from Github, defining weblink 
# pl.DataFrame(list_raw_files(repo_owner, repo_name, subfolder_path, branch)).filter(type='dir').unnest('_links').head(1).glimpse()
df_raw = pl.DataFrame(list_raw_files(repo_owner, repo_name, subfolder_path, branch)).filter(type='dir').unnest('_links').select('name', 'html')
df = df_raw.with_columns(
    qmd_file=pl.col.html+'/index.qmd', 
    qmd_file_raw='https://raw.githubusercontent.com/'+repo_owner+'/'+repo_name+'/'+branch+'/'+subfolder_path+'/'+pl.col.name+'/index.qmd', 
    weblink='https://inseefrlab.github.io/ssphub/pr-preview/pr-124/'+subfolder_path+'/'+pl.col.name
)

# Fetching doc metadata from YAML headers of the files
# Split the YAML header and the HTML content
prez = [pl.DataFrame({'qmd_file_raw': qmd_file_raw, 'yaml_dic': yaml.safe_load(fetch_qmd_file(qmd_file_raw).split('---', 2)[1])}, strict=False).unnest('yaml_dic') for qmd_file_raw in list(df['qmd_file_raw'])]
prez = [df.select(['qmd_file_raw', 'title', 'description', 'categories']) for df in prez]  # bcs polars doesnt like different data types / new columns ...
df = df.join(pl.concat(prez, how = 'diagonal_relaxed'), on='qmd_file_raw')

# Preparing posting to Grist table
variable_mapping = {
            'title': 'Titre',
            'qmd_file': 'Lien_vers_fichier_a_modifier',
            'description': 'Description',
            'weblink': 'Lien_sur_le_site',
            'categories': 'Categories'
            }

df_grist = (
    df\
        .with_columns(
            categories=pl.concat_list(pl.lit("L"), "categories")
        )  # To translate to Grist List types
        .rename(variable_mapping)  # To match Grist table column names
        .drop('html', 'name', 'qmd_file_raw')
)

# Add records to grist table
get_dinum_grist_login(os.environ['GRIST_SSPHUB_WEBSITE_MERGE_ID']).add_records('Retours', df_grist.to_dicts())
