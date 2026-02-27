# Objective

Tools to manage [SSPHub's](https://ssphub.netlify.app/) directory and [SSPHub's](https://ssphub.netlify.app/) newsletter system.

# Use

## Requirements

- Have access to GRIST directory
- Have environment variables :
  - GRIST_API_KEY : your API Key to use Grist (see [GRIST documentation](https://support.getgrist.com/rest-api/) to see how to access it)
  - GRIST_SSPHUB_DIRECTORY_ID : GRIST id of the SSPHub's Directory document (available on Grist)
  - GRIST_SSPHUB_WEBSITE_MERGE_ID : GRIST id of the internal table to merge old website to new website (available on Grist)
  - EMAIL_VALIDATION_TO, EMAIL_VALIDATION_CC, EMAIL_SSPHUB : email addresses

- Pour générer l'email de newsletter, les images doivent être stockées dans le repo git. Les images incluent directement avec des liens ne seront pas inclues dans l'email
- la newsletter doit être stockée dans un fichier "index.qmd" stocké dans infolettre/infolettre_XX où XX est le numéro de l'infolettre. Si pas là, le lien de la newsletter publiée dans l'email ne sera pas le bon.
- nom de la branche par défaut dans l'argument du script est 'newsletter_XX', avec le nom du folder où aller chercher le "index.qmd" identique.

## Step by step

### Newsletter

L'objectif ici est de valider et d'envoyer la newsletter du SSPHub aux membres inscrits sur Grist.

#### Validation de la newsletter :

- Faire une PR sur le site
- Envoyer le lien à RL, MH
- reprendre les commentaires
- Ouvrir Onyxia
- Avoir ce repo chargé
- `cd newsletter_tools`
- To generate email :
  - from the CLI, use uv run clearance.py with arguments. For example `uv run clearance.py -n 21 -b newsletter_21`
  - deprecated - You can also do it manually by going to script.py, and run function generate_email with Object. But it creates issues with working directory for css (file : email/css/style.css)
- download email
- add text to say It's the newsletter for clearance
- send it

#### Envoi de la newsletter

- Email :
  - To generate draft email :
    - from the CLI, use uv run main.py with arguments. For example `uv run main.py -n 21 -o "[SSPHub] - Infolettre 21 de décembre 2025"`
    - deprecated - You can also do it manually by going to script.py, and run function generate_email with Object.
      But it creates issues with working directory for css (file : email/css/style.css)
  - Download email
  - Check the newsletter (format, typos etc)
  - Select the right Outlook account
  - Deal with FMB and global lists (?)
  - Press Send
- Tchap :
  - to generate tchap message : from the CLI, use uv run tchap.py with infolettre nb as argument. For example `uv run main.py -n 23 `
  - copy paste txt stored in .temp/tchap_message.txt in the SSPHub Tchap group

#### Après envoi :

- Cleaning de la mailing list : copier tous les messages d'erreurs dans un fichier "replies.txt" placé dans le dossier parent newsletter_tools/
- Pour les supprimer :
  - from the CLI, use uv run treat_replies.py with file path as argument. For example `uv run treat_replies.py -f replies.txt`. By default, file is the replies.txt file located in newsletter_tools.
  - deprecated - Function delete_email_from_contact_table va extraire les emails et les supprimer de la table Contact de Grist.
    Fonctionne aussi avec des emails pas dans l'annuaire (ne fera rien du coup).

### Fusion site SSPHub / SSPLab

- (deprecated) To import draft template to SSPHub's site, go to script.py and run fill_all_templates_from_grist
