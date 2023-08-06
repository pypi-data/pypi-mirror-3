============
Did You Mean
============

Did You Mean provides you access to the Google's ``Did you Mean`` feature from your script.


    #!/usr/bin/env python

    import sys
	from didYouMean import didYouMean

	def main():
		spell = "Poshgresql"

		correctSpell = didYouMean.didYouMean(spell)

		print correctSpell

	if __name__ == "__main__":
		main()

